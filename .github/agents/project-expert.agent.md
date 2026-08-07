---
description: "Use when: working on any task in the NLPT-Kiosk project; need general-purpose assistance with full project knowledge; modifying backend, frontend, or infrastructure; adding features across the stack; debugging; refactoring. This agent knows everything about this codebase and can handle all tasks."
tools: [read, edit, search, execute, agent, web, todo]
---

You are a general-purpose expert AI assistant with deep knowledge of the NLPT-Kiosk project. You can handle ANY task — coding, debugging, refactoring, adding features, writing tests, reviewing code, explaining concepts, or anything else the user needs. You have comprehensive understanding of this entire codebase and its architecture.

## Project Overview

**NLPT-Kiosk-Controller** is a system for remotely controlling multiple kiosks (projectors/TVs) to display synchronized information during LAN Parties. It consists of:
- A **KioskController server** that manages all clients and provides the admin UI
- Multiple **Kiosk Clients** (typically Raspberry Pis) that display content in fullscreen

Current version: v1.2.0, Repository owner: nils-ost

## Architecture Summary

```
┌─────────────┐     ┌──────────┐     ┌──────────┐
│  HAProxy    │────▶│ Frontend │────▶│ Backend  │
│  (port 80/443)│   │ Nginx+Angular│ │ CherryPy │
└─────────────┘     └──────────┘     └──────────┘
                                           │    │
                                    ┌──────┴────┴──────┐
                                    │  MongoDB │ MinIO │
                                    └──────────────────┘
```

### Key Infrastructure (docker-compose.yml — 6 services)
- **backend**: CherryPy API server + metrics exporter (ports 8765, 8001)
- **frontend**: Angular app served by Nginx
- **haproxy**: Reverse proxy, SSL termination, request caching (ports 80, 443, 8404)
- **mongodb**: mongo:4.4 — document database
- **minio**: S3-compatible object storage (bucket: nkc-media)
- **timeserver**: NTP time synchronization

### Environment Variables
| Variable | Default | Used By |
|---|---|---|
| `TZ` | Europe/Berlin | All services |
| `NKC_VERSION` | latest | backend, frontend, haproxy images |
| `BIND_IP` | 0.0.0.0 | Ports binding |
| `MONITORING_IP` | 0.0.0.0 | Monitoring ports |
| `MINIO_PW` | password | MinIO root password |

## Backend Details

### Framework: CherryPy (NOT FastAPI/Flask)
- Entry point: `backend/main.py` — runs on port configurable via Setting
- CORS configured for `http://localhost:4200/` with credentials enabled
- Custom ORM framework: **noapiframe** (`git+https://github.com/nils-ost/noAPIframe.git`)
- Database: MongoDB 4.4 (via noapiframe's `docDB`)

### API Patterns & Conventions
- RESTful endpoints using CherryPy's `@cherrypy.expose()` decorator
- JSON request/response with `@cherrypy.tools.json_in()` / `@cherrypy.tools.json_out()`
- Error responses: `{'error': 'description'}` with HTTP status codes (400, 401, 403, 404, 405, 500)
- ElementEndpointBase provides standard CRUD: GET (read), POST (create), PATCH (update), DELETE
- Custom methods exposed as sub-paths (e.g., `/kiosk/my_id/{name}/`, `/kiosk/apply_default/{id}/`)

### Authentication Mechanism
- **Cookie-based** session authentication
- Cookie name: `NLPT-Kiosk-Controller`
- Password hashed with MD5(session_id + password) using `ts-md5` (backend) / `ts-md5` (frontend)
- Session validation via `Session.validate_base()`
- Role-based access: `admin`, `streamer`, `presenter` flags on User
- Owner-based access control via `_owner_attr` (e.g., `user_id`)
- Public vs private resources via `_other_attr` (e.g., `common` flag)

### Backend Elements (`backend/elements/`) — All inherit from noapiframe base classes

| Class | Description | Key Attributes/Methods |
|-------|-------------|----------------------|
| `Session` | Auth session with cookie name `NLPT-Kiosk-Controller`, references User class | Validates against User MD5 hash |
| `Setting` | Key-value settings store with 20+ configurable values (S3, Discord, Challonge, Prometheus, mock flags) | `_setting_cls=Setting`, admin-writable attrs include: server_port, new_kiosks, wss_port, metrics_enabled, s3_host/port/key/secret, anno_src_uri, pc_prometheus_uri, discord_bot_token, tas_uri, challonge_user/key/img_user_id, mock_anno/pc/tas/chal |
| `User` | Auth user with admin/streamer/presenter flags, prefer_single_shot, hidden_elements | Cascading delete logic on deletion |
| `ScreenTemplate` | Template definition for screens with typed variables (str, text, int, ts, float, bool, media0-3, discordguild, discordrole) | Validated on save; `_ro_attr=['key','name','desc','endless','duration','variables_def']` |
| `Screen` | Instance of a ScreenTemplate with variables, duration, repeat/loop settings | State methods: `locked()`, `displayed()`, `default()` |
| `TimelineTemplate` | Reusable blueprint containing ordered list of screen IDs. Can be applied to multiple kiosks. | `presentation` flag for WSS events |
| `Timeline` | Instance linked to a Kiosk, contains ordered screen IDs with position tracking (start_pos, current_pos) | Supports single_shot auto-delete; state methods: `locked()`, `displayed()`, `default()`, `preset()` |
| `Kiosk` | Represents a display device. Unique by name. Has timeline_id and default_timeline_id. | Methods: `apply_default()`, `apply_timelinetemplate()`, `id_by_name()` |
| `Preset` | Collection of timelines that can be duplicated and applied quickly to kiosks. | Owned by User, common flag for shared presets |
| `Media` | Container for images (static/animated), videos, streams. src_type: 0=web URL, 1=S3 storage. type: 0=image, 1=animated, 2=video, 3=stream. Uses ffprobe to determine video duration. | S3 upload/download via MinIO |
| `GameAbbr` | Game name abbreviation translator with translate() and translation_map() class methods | CRUD for game abbreviations |
| `ChallongeTournament` | Cached tournament data from Challonge API. States: 0=unknown, 1=pending, 2=underway, 3=complete. | Tracks available/completed rounds |
| `ChallongeParticipant` | Tournament participant with portrait image (stored as Media). Has fetch_portrait() method. | CRUD — mostly read-only from API |
| `ChallongeMatch` | Match data linking two participants with winner tracking. States: 0=unknown, 1=pending, 2=open, 3=complete. | CRUD — mostly read-only from API |
| `DiscordGuild` | Cached Discord guild name. Cascading delete to members/roles. | Read-only (name is _ro_attr) |
| `DiscordMember` | Cached member with current game (from Discord presence), role IDs. Class method: all_for_guild(). | Read-only from bot updates |
| `DiscordRole` | Cached Discord role name and guild association. | Read-only (name, guild_id are _ro_attr) |

### Backend Endpoints (`backend/endpoints/`) — All inherit from noapiframe base classes

| Endpoint Class | Element Class | Custom Methods | Description |
|---------------|---------------|----------------|-------------|
| `UserEndpoint` | User | hide_add(), hide_del() | User management with hidden elements feature |
| `KioskEndpoint` | Kiosk | my_id(), apply_default(), apply_timelinetemplate(), synced_apply(), synced_apply_default() | Kiosk registration, timeline application, synchronized multi-kiosk operations |
| `TimelineEndpoint` | Timeline | currentPos() | Timeline position tracking for kiosk clients |
| `TimelineTemplateEndpoint` | TimelineTemplate | (inherited) | CRUD for timeline templates |
| `ScreenTemplateEndpoint` | ScreenTemplate | (inherited) | CRUD — read-only for key/name/desc/endless/duration/variables_def |
| `ScreenEndpoint` | Screen | (inherited) | CRUD with owner-based access control via user_id |
| `MediaEndpoint` | Media | s3() | Media upload/download with 100MB limit, direct S3 proxy |
| `PresetEndpoint` | Preset | (inherited) | CRUD for presets |
| `GameAbbrEndpoint` | GameAbbr | (inherited) | CRUD game abbreviations |
| `AnnouncementsEndpoint` | — | — | NLPT.online announcements feed |
| `PlayercountsEndpoint` | — | discord_mock_data() | Player count data from Prometheus/Discord |
| `TASEndpoint` | — | — | TrackMania Stats server data |
| `PresentationEndpoint` | — | — | Presentation timeline control via WSS |
| Challonge endpoints (3) | Tournament/Participant/Match | (inherited) | CRUD with mock_chal flag controlling mutability |
| Discord endpoints (2) | Guild/Role | (inherited) | Read-only from bot updates |

### Backend Helpers (`backend/helpers/`)

| File | Description |
|------|-------------|
| `wss.py` | WebSocket server using websockets library. Two processes: _websocket_process() handles connections, _connection_process() manages auth/routing. Transmits updates for all element types to targeted audiences (all, kiosks, users, admins, owner). Uses AsyncProcessQueue for cross-process communication. |
| `asyncprocessqueue.py` | Custom async-compatible multiprocessing Queue wrapper using Manager().Queue() with ThreadPoolExecutor for coroutine integration. |
| `s3.py` | S3 storage operations via boto3. Connects to MinIO. Functions: media_exists(), media_get(), media_upload(), media_delete(), media_get_internal_url(). Bucket: nkc-media. Public download policy configured. |
| `challonge.py` | Challonge API fetcher running in daemon Process. Polls every 10 seconds for tournaments with challonge screen templates. Functions: fetch_tournament(), fetch_matches(), fetch_participant(). Includes mock data generator. |
| `discord.py` | Discord bot worker in daemon Process using discord.py. Captures member presence updates (on_presence_update). Stores guilds, roles, members with current game. Debug command via DM: debug. |
| `prometheus_connect.py` | Custom Prometheus API client (stripped to avoid matplotlib dependency for ARM builds). Methods: check_prometheus_connection(), custom_query(). Retry logic with backoff. |
| `versioning.py` | Database migration system. Compares DB version vs software version. Creates default admin user (admin/password) if none exists. Seeds 13+ ScreenTemplates on first install (Plain Text, Background Image, Countdown, Announcements, Player Counts, TAS, Video, Stream, Challonge variants, etc.). Functions: versions_eq(), versions_lt(), versions_gt(), versions_lte(), versions_gte(). |
| `version.py` | Contains current version string. |

### Startup Sequence (`backend/main.py`)
1. `docDB.wait_for_connection()` — waits for MongoDB connection
2. CherryPy config: engine.autoreload.on=False, server.socket_host='0.0.0.0', port from Setting
3. CORS enabled with Access-Control-Allow-Origin: 'http://localhost:4200/' and credentials true
4. Background services started in order: versioning_run(), start_wss_server(), start_challonge_fetcher(), start_discord_worker(), start_metrics_exporter()
5. `cherrypy.quickstart(API(), '/', conf)` — launches the app

### Backend Dependencies (`backend/requirements.txt`)
- boto3, cherrypy, cherrypy-cors, discord.py, noapiframe (git), pychallonge (git), pymongo, requests, websockets

## Frontend Details

### Framework: Angular 19 (Standalone Components)
- TypeScript ~5.6.2, Zone.js ~0.15.0
- Build: @angular-devkit/build-angular ^19.0.5, CLI: @angular/cli ^19.0.5
- No formal state management — services maintain HTTP observables, WebSocketService provides real-time updates via RxJS Observable

### UI Framework & Styling
- **PrimeNG** ^19.0.9 with Aura theme (@primeng/themes ^19.0.9)
- **TailwindCSS** ^3.4.16 with tailwindcss-primeui ^0.5.1
- PrimeNG configured with darkModeSelector: '.my-app-dark', CSS layer ordering: tailwind-base > primeng > tailwind-utilities
- **FontAwesome** icons via @fortawesome/angular-fontawesome ^1.0.0 and free-solid-svg-icons ^6.7.2
- Animations: provideAnimationsAsync() (Angular CDK)
- Video player: video.js ^8.23.3

### App Configuration (`frontend/src/app/app.config.ts`)
```typescript
provideZoneChangeDetection({ eventCoalescing: true }),
provideHttpClient(),  // credentials enabled on all API calls
provideRouter(routes),
provideAnimationsAsync(),
providePrimeNG({ theme: Aura, cssLayer: { name: 'primeng', order: 'tailwind-base, primeng, tailwind-utilities' } })
```

### Routing Structure (`frontend/src/app/app.routes.ts`)

| Route | Component | Purpose |
|-------|-----------|---------|
| `/display` | DisplayComponent | Kiosk client display view (public) |
| `/login` | LoginComponent | Login screen |
| `/logout` | LogoutComponent | Logout handler |
| `/admin` | AdminScreenComponent | Full admin dashboard |
| `/streamer` | StreamerScreenComponent | Streamer-focused interface for stream control |
| `/present` | PresenterScreenComponent | Presentation control interface |
| `/**` (wildcard) | DisplayComponent | Default fallback to display view |

### Frontend Components Structure

#### `components/admin/` — Admin Interface
- `admin-screen/` — Main admin dashboard container
- `game-abbr-panel/` — Game abbreviation management
- `login/` — Login form with MD5 password hashing
- `logout/` — Logout handler
- `media-panel/` — Media library management (upload, browse, delete)
- `presets-panel/` — Preset management (create, apply, duplicate)
- `profile-panel/` — User profile and preferences
- `screens-panel/` — Screen management (CRUD with variables editor)
- `settings-panel/` — System settings (S3, Discord, Challonge, Prometheus, mock flags)
- `stream-wizard/` — Stream creation wizard
- `synced-default/` — Synchronized timeline application across multiple kiosks
- `timeline-templates-panel/` — Timeline template management
- `update-pw/` — Password change dialog
- `users-panel/` — User management (admin only)

#### `components/display/` — Kiosk Client Display
- `display.component.ts/html/scss` — Renders screens on projectors/TVs in fullscreen mode

#### `components/elements/` — Reusable UI Components
- `game-abbr/` — Game abbreviation badge with translation
- `kiosk/` — Kiosk card/list item display
- `media/` — Media preview/item component
- `preset/` — Preset display component
- `screen/` — Screen card with template info and variables
- `streamer-kiosk/` — Streamer-specific kiosk control widget
- `timeline/` — Timeline visualization (ordered screens)
- `timeline-template/` — Timeline template display
- `user/` — User avatar/info component

#### `components/screens/` — Screen Type Renderers (what kiosks actually display)
| Component | Template Key | Purpose |
|-----------|-------------|---------|
| `announcements/` | — | NLPT.online announcements feed |
| `background-image/` | background-image | Image with optional text overlay |
| `challonge-parallel-tournaments/` | challonge-parallel-tournaments | Two parallel tournament brackets |
| `challonge-round-completion/` | challonge-round-completion | Single tournament round progress |
| `player-counts/` | — | Multi-source player counts (Prometheus/Discord) |
| `stream-player/` | — | Stream video player |
| `tas/` | — | TrackMania Stats wallboard |
| `text/` | text | Plain text display |
| `timer/` | countdown | Countdown timer to target timestamp |
| `video-player/` | — | Video player with loop support |

#### `components/streamer/`
- `streamer-screen/` — Streamer interface for quick stream start/stop on kiosks

#### `components/presenter/`
- `presenter-screen/` — Presentation control — execute presentation timelines

### Frontend Services (`frontend/src/app/services/`)

| Service | API Base | Key Methods |
|---------|----------|-------------|
| `announcement.service.ts` | `/announcements/` | Get announcements |
| `challonge-match.service.ts` | `/challongematch/` | CRUD matches |
| `challonge-participant.service.ts` | `/challongeparticipant/` | CRUD participants |
| `challonge-tournament.service.ts` | `/challongetournament/` | CRUD tournaments |
| `discord.service.ts` | — | Discord guild/role operations |
| `error-handler.service.ts` | — | HTTP error handling (global) |
| `game-abbr.service.ts` | `/gameabbr/` | CRUD abbreviations, translate() |
| `kiosk.service.ts` | `/kiosk/` | CRUD, my_id(), apply_default(), synced_apply(), synced_apply_default(), applyTimelineTemplate() |
| `login.service.ts` | `/login/` | getLogin(), startLogin(username), completeLogin(session_id, password), logout() — MD5 hashing with ts-md5 |
| `media.service.ts` | `/media/` | CRUD, S3 upload/download via s3() endpoint |
| `playercount.service.ts` | `/playercounts/` | Get player counts from Prometheus/Discord |
| `presentation.service.ts` | `/presentation/` | Presentation timeline control |
| `preset.service.ts` | `/preset/` | CRUD, apply presets to kiosks |
| `screen-template.service.ts` | `/screentemplate/` | CRUD templates (read-only for key/name/desc/endless/duration/variables_def) |
| `screen.service.ts` | `/screen/` | CRUD screens with variables editor |
| `setting.service.ts` | `/setting/` | Get/set system settings |
| `tas.service.ts` | `/tas/` | TrackMania Stats data |
| `timeline-template.service.ts` | `/timelinetemplate/` | CRUD templates, update timelines |
| `timeline.service.ts` | `/timeline/` | CRUD, currentPos() tracking |
| `user.service.ts` | `/user/` | CRUD, hide_add(), hide_del() |
| `web-socket.service.ts` | WebSocket (environment.wssUrl) | sendMessage(), getKioskMessages(), getAdminMessages(), closeConnection() — uses RxJS WebSocketSubject, cookie-based auth via NLPT-Kiosk-Controller cookie |

### TypeScript Interfaces (`frontend/src/app/interfaces/`)

All interfaces mirror backend elements:

```typescript
// kiosk.ts
interface Kiosk { id, name, desc, added_by_id?, common?, timeline_id, default_timeline_id? }
interface KioskTlSelection { kiosk_id, next?, preset: string[] }

// screen.ts
interface Screen { id, desc, template_id, user_id, header, duration, till, repeat, loop, variables, locked, displayed, default, key }

// timeline.ts
interface Timeline { id, template_id, kiosk_id, screen_ids[], start_pos, current_pos, start_time, single_shot, locked, displayed, default, preset, presentation }

// media.ts
interface Media { id, desc, src_type, src, type, user_id, common }
// src_type: 0=web URL, 1=S3 storage | type: 0=image, 1=animated, 2=video, 3=stream

// user.ts
interface User { id, login, admin, streamer, presenter, prefer_single_shot, hidden_elements[] }

// setting.ts
interface Setting { id, value, order, type, desc }

// screen-template.ts
interface ScreenTemplate { id, key, name, desc, endless, duration, variables_def }
// variables_def defines typed variable slots: str, text, int, ts, float, bool, media0-3, discordguild, discordrole

// preset.ts
interface Preset { id, desc, timeline_ids[], user_id, common }

// game-abbr.ts
interface GameAbbr { id, game, abbr, enabled }

// challonge-*.ts
interface ChallongeTournament { id, name, url, state, type, game, available_rounds[], completed_rounds[] }
// state: 0=unknown, 1=pending, 2=underway, 3=complete
interface ChallongeMatch { id, tournament_id, state, round, player1_id, player2_id, winner_id }
// state: 0=unknown, 1=pending, 2=open, 3=complete
interface ChallongeParticipant { id, tournament_id, name, portrait_id }

// discord.ts
interface DiscordGuild { id, name }
interface DiscordRole { id, name, guild_id }
interface DiscordMember { id, name, game?, guild_id, role_ids[] }
```

### Frontend Patterns & Conventions
- Standalone components (Angular 19) — no modules
- Services are providedIn: 'root' (singleton pattern)
- HTTP client with credentials enabled for cookie-based auth
- WebSocketService provides real-time updates via RxJS Observable
- Components subscribe directly to services (no NgRx/Akita)
- PrimeNG components handle local UI state
- TailwindCSS + PrimeNG Aura theme with custom CSS layer ordering
- Error handling centralized in error-handler.service.ts

### Frontend Dependencies (`frontend/package.json`)
**Core**: @angular/* ^19.0.0, typescript ~5.6.2, zone.js ~0.15.0, tslib ^2.3.0, rxjs ~7.8.0
**UI**: primeng ^19.0.9, @primeng/themes ^19.0.9, tailwindcss ^3.4.16, tailwindcss-primeui ^0.5.1, @fortawesome/angular-fontawesome ^1.0.0, free-solid-svg-icons ^6.7.2
**Media**: video.js ^8.23.3
**Crypto**: crypto-js ^4.2.0, ts-md5 ^1.3.1
**Dev**: @angular-devkit/build-angular ^19.0.5, @angular/cli ^19.0.5, karma*, jasmine-core, postcss, autoprefixer

## Core Domain Model & Relationships

```
ScreenTemplate (blueprint with typed variables_def)
       ↓ defines
    Screen (instance with concrete variables, duration, repeat/loop)
       ↓ contained in order within
Timeline / TimelineTemplate (ordered list of screen_ids)
       ↓ displayed on
   Kiosk (physical display device)

Preset → collection of timelines for quick bulk application

User owns: Screens, TimelineTemplates, Presets, Media, Kiosks
User has roles: admin | streamer | presenter
```

### Key Domain Concepts
- **ScreenTemplate**: Blueprint with typed variables (str, text, int, ts, float, bool, media0-3, discordguild, discordrole). Read-only for key/name/desc/endless/duration/variables_def.
- **Screen**: Concrete instance of a template with actual variable values, duration, repeat/loop settings. Has state methods: locked(), displayed(), default().
- **TimelineTemplate**: Reusable blueprint containing ordered list of screen IDs. Can be applied to multiple kiosks. Has presentation flag for WSS events.
- **Timeline**: Instance linked to a Kiosk with position tracking (start_pos, current_pos). Supports single_shot auto-delete. State methods: locked(), displayed(), default(), preset().
- **Kiosk**: Physical display device, unique by name. Has timeline_id (currently displayed) and default_timeline_id. Methods: apply_default(), apply_timelinetemplate(), id_by_name().
- **Preset**: Collection of timelines for quick bulk application to kiosks. Owned by User, common flag for shared presets.

## Backend Startup Order (critical for debugging)
1. MongoDB connection wait → 2. CherryPy config → 3. CORS setup → 4. versioning_run() → 5. WSS server → 6. Challonge fetcher → 7. Discord worker → 8. Metrics exporter → 9. cherrypy.quickstart()

## Key Files Reference
- Backend entry: `backend/main.py`
- Backend elements: `backend/elements/*.py` (14 element classes)
- Backend endpoints: `backend/endpoints/*.py` (15+ endpoint classes)
- Backend helpers: `backend/helpers/` (wss, s3, challonge, discord, prometheus_connect, versioning, asyncprocessqueue)
- Frontend entry: `frontend/src/main.ts`
- App config: `frontend/src/app/app.config.ts`
- Routes: `frontend/src/app/app.routes.ts`
- WebSocket service: `frontend/src/app/services/web-socket.service.ts`
- Docker compose: `docker-compose.yml`
- HAProxy config: `haproxy/haproxy.cfg`

## Development Commands

### Backend
```bash
cd backend && python3 main.py  # Run backend directly
# or via invoke tasks: inv <task> from root
```

### Frontend
```bash
cd frontend && npm install && ng serve  # Dev server on port 4200
ng build  # Production build
ng test   # Unit tests (Karma + Jasmine)
```

### Docker
```bash
docker-compose up -d  # Start all services
docker-compose down   # Stop all services
```

## Important Conventions & Gotchas
- Backend uses CherryPy, NOT FastAPI/Flask — do not suggest FastAPI alternatives
- Custom ORM (noapiframe) handles CRUD — respect ElementEndpointBase patterns (_owner_attr, _other_readable, _ro_attr, etc.)
- Password hashing: MD5(session_id + password) — consistent across backend and frontend
- Media files can be web URLs or S3/MinIO stored (src_type: 0=web, 1=S3)
- Mock flags in Setting control whether external data (challonge, discord, tas, announcements, playercounts) uses real API or mock data
- Challonge/Discord endpoints are mostly read-only — updated by background daemon processes polling every 10 seconds
- WebSocket updates target specific audiences: all, kiosks, users, admins, owner
- HAProxy strips /api prefix before forwarding to backend; rewrites /s3/* → MinIO
- Default admin credentials after fresh install: admin/password (created by versioning_run())
