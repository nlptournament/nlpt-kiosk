# NLPT-Kiosk Project Context

This project is **NLPT-Kiosk-Controller** — a system for remotely controlling multiple kiosks (projectors/TVs) to display synchronized information during LAN Parties. Current version: v1.1.0, Repository owner: nils-ost.

## Architecture Overview

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

### Docker Services (docker-compose.yml — 6 services)
- **backend**: CherryPy API server + metrics exporter + stream health worker daemon (ports 8765, 8001)
- **frontend**: Angular app served by Nginx
- **haproxy**: Reverse proxy, SSL termination, request caching (ports 80, 443, 8404)
- **mongodb**: mongo:4.4 — document database
- **minio**: S3-compatible object storage (bucket: nkc-media)
- **timeserver**: NTP time synchronization

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | CherryPy, noapiframe ORM, MongoDB 4.4 |
| Frontend | Angular 19 (standalone), TypeScript ~5.6, PrimeNG 19, TailwindCSS |
| Infra | Docker Compose, HAProxy, Nginx, MinIO |

## Backend Conventions

- **CherryPy** — NOT FastAPI/Flask. Endpoints use `@cherrypy.expose()` decorator.
- RESTful JSON API with `@cherrypy.tools.json_in()` / `@cherrypy.tools.json_out()`.
- Error responses: `{'error': 'description'}` with HTTP status codes (400, 401, 403, 404, 405, 500).
- Custom ORM **noapiframe** — elements inherit from base classes; endpoints use ElementEndpointBase patterns (`_owner_attr`, `_other_readable`, `_ro_attr`).
- Standard CRUD: GET (read), POST (create), PATCH (update), DELETE. Custom methods as sub-paths.

### Authentication
- Cookie-based session auth. Cookie name: `NLPT-Kiosk-Controller`.
- Password hashed with MD5(session_id + password) using ts-md5 (both backend and frontend).
- Role-based access: `admin`, `streamer`, `presenter` flags on User.
- Owner-based access control via `_owner_attr`; public vs private via `_other_attr` (e.g., `common` flag).

### Key Domain Model
```
ScreenTemplate → Screen → Timeline/TimelineTemplate → Kiosk
Preset → collection of timelines for quick bulk application
User owns: Screens, TimelineTemplates, Presets, Media, Kiosks
```

- **ScreenTemplate**: Blueprint with typed variables (str, text, int, ts, float, bool, media0-3, discordguild, discordrole).
- **Screen**: Concrete instance with variable values, duration, repeat/loop settings. State: locked(), displayed(), default().
- **TimelineTemplate**: Reusable ordered list of screen IDs. Has `presentation` flag for WSS events.
- **Timeline**: Instance linked to a Kiosk with position tracking (start_pos, current_pos). Supports single_shot auto-delete and jump-to functionality.
- **Kiosk**: Physical display device, unique by name. Has `participant` flag (bool, default False — when True kiosk is listed in Participant Interface).
- **Media**: Images, videos, streams, other. src_type: 0=web URL, 1=S3 storage. type: 0=image, 1=animated, 2=video, 3=stream, 4=other.

### Background Services (started in order at boot)
versioning → WSS server → Challonge fetcher → Discord worker → Stream health worker → Metrics exporter

### External Integrations
- **Challonge**: Tournament data polled every 10 seconds via daemon process.
- **Discord**: Bot captures member presence updates, stores guilds/roles/members with current game.
- **Prometheus**: Player count queries (custom client, no matplotlib for ARM compatibility).
- **MinIO/S3**: Media storage and upload/download.

## Frontend Conventions

- Angular 19 standalone components — no modules. Services are `providedIn: 'root'`.
- HTTP client with credentials enabled for cookie-based auth.
- Real-time updates via WebSocketService (RxJS Observable). Components subscribe directly to services (no NgRx/Akita).
- PrimeNG + TailwindCSS Aura theme with CSS layer ordering: tailwind-base > primeng > tailwind-utilities.
- Error handling centralized in error-handler.service.ts.

### Key Routes
| Route | Purpose |
|-------|---------|
| `/display` | Kiosk client display view (public) |
| `/admin` | Full admin dashboard |
| `/streamer` | Stream control interface |
| `/present` | Presentation control interface |
| `/participant` | Public-facing UI for LAN party participants |

## Important Gotchas
- Backend uses CherryPy, NOT FastAPI/Flask — do not suggest FastAPI alternatives.
- Mock flags in Setting control whether external data (challonge, discord, tas, announcements) uses real API or mock data.
- HAProxy strips `/api` prefix before forwarding to backend; rewrites `/s3/*` → MinIO.
- Default admin credentials after fresh install: admin/password.
