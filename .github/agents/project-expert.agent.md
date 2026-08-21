---
description: "Use when: working on any task in the NLPT-Kiosk project; need general-purpose assistance with full project knowledge; modifying backend, frontend, or infrastructure; adding features across the stack; debugging; refactoring. This agent knows everything about this codebase and can handle all tasks."
tools: [read, edit, search, execute, agent, web, todo]
---

You are a general-purpose expert AI assistant with deep knowledge of the NLPT-Kiosk project. You can handle ANY task — coding, debugging, refactoring, adding features, writing tests, reviewing code, explaining concepts, or anything else the user needs. You have comprehensive understanding of this entire codebase and its architecture.

> **Shared context**: General project overview, architecture, conventions, and domain model are in `.github/copilot-instructions.md`. This file contains deep reference details for backend elements, endpoints, helpers, frontend components/services/interfaces, and workflow-specific knowledge.

## Deep Reference: Backend Elements (`backend/elements/`)

All inherit from noapiframe base classes. See `.github/copilot-instructions.md` for domain model overview.

| Class | Description | Key Attributes/Methods |
|-------|-------------|----------------------|
| `Session` | Auth session with cookie name `NLPT-Kiosk-Controller`, references User class | Validates against User MD5 hash |
| `Setting` | Key-value settings store with 20+ configurable values (S3, Discord, Challonge, Prometheus, mock flags) | `_setting_cls=Setting`, admin-writable attrs include: server_port, new_kiosks, participant_interface, wss_port, metrics_enabled, s3_host/port/key/secret, anno_src_uri, pc_prometheus_uri, discord_bot_token, tas_uri, challonge_user/key/img_user_id, mock_anno/pc/tas/chal |
| `User` | Auth user with admin/streamer/presenter flags, prefer_single_shot, hidden_elements | Cascading delete logic on deletion |
| `ScreenTemplate` | Template definition for screens with typed variables (str, text, int, ts, float, bool, media0-3, discordguild, discordrole, tt) | Validated on save; `_ro_attr=['key','name','desc','endless','duration','variables_def']` |
| `Screen` | Instance of a ScreenTemplate with variables, duration, repeat/loop settings | State methods: `locked()`, `displayed()`, `default()` |
| `TimelineTemplate` | Reusable blueprint containing ordered list of screen IDs. Can be applied to multiple kiosks. | `presentation` flag for WSS events, `import_pdf(pdf_media, prefix, png_width)` — converts a PDF (Media type=4) into Screens using the "Background Image" template; creates Media elements (type=0) and Screen instances per page |
| `Timeline` | Instance linked to a Kiosk, contains ordered screen IDs with position tracking (start_pos, current_pos) | Supports single_shot auto-delete; state methods: `locked()`, `displayed()`, `default()`, `preset()`; **jump-to**: `check_for_jump()` — when `current_pos % 2 == 1` and the screen at that position has template key 'jump-to', either applies default timeline or a specified TimelineTemplate |
| `Kiosk` | Represents a display device. Unique by name. Has timeline_id and default_timeline_id. | Attributes include: `participant` (bool, default False — when True kiosk is listed in Participant Interface). Methods: `apply_default()`, `apply_timelinetemplate(template_id)`, `id_by_name()` |
| `Preset` | Collection of timelines that can be duplicated and applied quickly to kiosks. | Owned by User, common flag for shared presets |
| `Media` | Container for images (static/animated), videos, streams, other. src_type: 0=web URL, 1=S3 storage. type: 0=image, 1=animated, 2=video, 3=stream, 4=other. Uses ffprobe to determine video duration. | Computed `active()` method — returns True for non-streams; returns False for streams (actual health status is determined by the stream_health worker and broadcast via WSS). Overrides `json()` to include `active` in responses. S3 upload/download via MinIO |
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
| `KioskEndpoint` | Kiosk | my_id(), apply_default(), apply_timelinetemplate(), synced_apply(), synced_apply_default() | Kiosk registration, timeline application, synchronized multi-kiosk operations. `_other_readable` includes `participant`; `_all_readable` includes `participant`; `_other_createable` includes `participant`; `_other_updateable` includes `participant` |
| `TimelineEndpoint` | Timeline | currentPos() — also calls `check_for_jump()` on the timeline after position update | Timeline position tracking for kiosk clients |
| `TimelineTemplateEndpoint` | TimelineTemplate | (inherited), `update_timelines()`, `import_pdf()` — converts a PDF Media into Screens using the "Background Image" template; requires admin or owner access |
| `ScreenTemplateEndpoint` | ScreenTemplate | (inherited) | CRUD — read-only for key/name/desc/endless/duration/variables_def |
| `ScreenEndpoint` | Screen | (inherited) | CRUD with owner-based access control via user_id |
| `MediaEndpoint` | Media | s3() | Media upload/download with 100MB limit, direct S3 proxy. `_other_readable` and `_all_readable` include `active` (computed stream health status) |
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
| `wss.py` | WebSocket server using websockets library. Two processes: _websocket_process() handles connections, _connection_process() manages auth/routing. Transmits updates for all element types to targeted audiences (all, kiosks, users, admins, owner). Uses AsyncProcessQueue for cross-process communication. Function `transmit_media_health(media, active)` — broadcasts minimal stream health payload `{media_id, active, content: 'stream_health'}` to ALL connected clients |
| `asyncprocessqueue.py` | Custom async-compatible multiprocessing Queue wrapper using Manager().Queue() with ThreadPoolExecutor for coroutine integration |
| `s3.py` | S3 storage operations via boto3. Connects to MinIO. Functions: media_exists(), media_get(), media_upload(), media_delete(), media_get_internal_url(). Bucket: nkc-media |
| `challonge.py` | Challonge API fetcher running in daemon Process. Polls every 10 seconds for tournaments with challonge screen templates. Functions: fetch_tournament(), fetch_matches(), fetch_participant() |
| `discord.py` | Discord bot worker in daemon Process using discord.py. Captures member presence updates (on_presence_update). Stores guilds, roles, members with current game |
| `prometheus_connect.py` | Custom Prometheus API client (stripped to avoid matplotlib dependency for ARM builds) |
| `stream_health.py` | Stream health detection daemon Process using ffprobe. Polls every 10 seconds all Media elements where type=3 and src_type=0 (web URL streams). Calls `transmit_media_health(media, active)` via WSS |
| `versioning.py` | Database migration system. Creates default admin user if none exists. Seeds 14+ ScreenTemplates on first install. Includes v1.2.0 migration adding `header_pos` and `header_size` variables to Stream ScreenTemplates |
| `version.py` | Contains current version string |

### Backend Dependencies (`backend/requirements.txt`)
boto3, cherrypy, cherrypy-cors, discord.py, noapiframe (git), pdf2image, pychallonge (git), pymongo, requests, websockets

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

### Routing Structure (`frontend/src/app/app.routes.ts`)

| Route | Component | Purpose |
|-------|-----------|---------|
| `/display` | DisplayComponent | Kiosk client display view (public). Auto-reroutes to `/participant` if Setting `participant_interface` is enabled and no kiosk name provided. |
| `/login` | LoginComponent | Login screen |
| `/logout` | LogoutComponent | Logout handler |
| `/admin` | AdminScreenComponent | Full admin dashboard. Menubar includes Participant Interface shortcut (visible when `participant_interface` setting is True). |
| `/streamer` | StreamerScreenComponent | Streamer-focused interface for stream control |
| `/present` | PresenterScreenComponent | Presentation control interface |
| `/participant` | ParticipantInterfaceComponent | **NEW** — Public-facing UI for unauthorized users to browse available kiosks and streams. Shows kiosk cards grid + active streams grid with WSS-reactive health indicators. |
| `/participant/stream/:screenId` | StreamViewerComponent | **NEW** — Dedicated stream viewer page opened in new tab from participant interface. Shows StreamPlayerComponent with controls enabled. |
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
- `presentation-wizard/` — PDF-to-Timeline import wizard (select user, select/upload PDF, choose target TimelineTemplate, set image width)

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
| `stream-player/` | stream-player | Stream video player with optional text header overlay via videojs-overlay plugin. Uses `header`, `header_pos`, and `header_size` template variables for positioning/sizing of overlayed text. Header position maps to Tailwind classes (e.g., 'top-left' → 'top-0 text-left'). New input: `showControls = input(false)` — when true, enables video.js control-bar for participant viewing while keeping display mode hidden. |
| `tas/` | — | TrackMania Stats wallboard |
| `text/` | text | Plain text display |
| `timer/` | countdown | Countdown timer to target timestamp |
| `video-player/` | — | Video player with loop support |

#### `components/streamer/`
- `streamer-screen/` — Streamer interface for quick stream start/stop on kiosks

#### `components/presenter/`
- `presenter-screen/` — Presentation control — execute presentation timelines

#### `components/participant/`
- `participant-interface/` — Public-facing UI for LAN party participants. Shows two sections: (1) Available Kiosks grid with status dots and external link icons, (2) Active Streams grid with pulsing green live indicators. Filters kiosks by `participant===true`, filters streams by template + WSS health status. Uses `streamHealth` Map for reactive stream health updates. Auto-checks `participant_interface` setting — navigates to `/admin` if disabled.
- `stream-viewer/` — Dedicated stream viewer opened in new tab from participant interface. Fetches screen by route param, shows StreamPlayerComponent with `[showControls]=true`. Handles 404 error state.

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
| `web-socket.service.ts` | WebSocket (environment.wssUrl) | sendMessage(), getKioskMessages(), getAdminMessages(), closeConnection() — uses RxJS WebSocketSubject, cookie-based auth via NLPT-Kiosk-Controller cookie. Frontend handles new `'stream_health'` content type messages from WSS containing `{media_id, active}` for reactive stream health updates. |

### TypeScript Interfaces (`frontend/src/app/interfaces/`)

All interfaces mirror backend elements:

```typescript
// kiosk.ts
interface Kiosk { id, name, desc, added_by_id?, common?, participant: boolean, timeline_id, default_timeline_id? }
interface KioskTlSelection { kiosk_id, next?, preset: string[] }

// screen.ts
interface Screen { id, desc, template_id, user_id, header, duration, till, repeat, loop, variables, locked, displayed, default, key }

// timeline.ts
interface Timeline { id, template_id, kiosk_id, screen_ids[], start_pos, current_pos, start_time, single_shot, locked, displayed, default, preset, presentation }

// media.ts
interface Media { id, desc, src_type, src, type, user_id, common, active: boolean }
// src_type: 0=web URL, 1=S3 storage | type: 0=image, 1=animated, 2=video, 3=stream, 4=other
// active: computed stream health status (True for non-streams; from WSS stream_health messages for streams)

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
