<!-- NOTE: This is a project-planner agent savepoint. Load with the `project-planner` agent to continue work. -->

# Participant Interface Implementation Plan

Session started: 2026-08-14

## Overview

The **ParticipantInterface** is a public-facing UI for unauthorized users (LAN party participants) to browse available kiosks and streams, without needing to log in. It provides an alternative to relying solely on the content projected on stage.

---

## Chapter 1: Backend — Add `participant` attribute to Kiosk ✅ DONE

Add a boolean flag to control which kiosks are listed in the Participant Interface.

### Changes Required

**1. `backend/elements/kiosk.py`**
- Add docstring line describing the new attribute
- Add to `_attrdef`: `participant=ElementBase.addAttr(type=bool, default=False, notnone=True)`

**2. `backend/endpoints/kiosk.py`**
Add `'participant'` to these four lists:
| List | Purpose |
|------|---------|
| `_other_readable` | Logged-in non-owner users can read it |
| `_all_readable` | Unauthorized visitors can read it (they need to see available kiosks) |
| `_other_createable` | Creators can set it on creation |
| `_other_updateable` | Logged-in non-owner users can update it |

Do **NOT** add to: `_all_updateable`, `_admin_updateable`, `_ro_attr`.

**3. `frontend/src/app/interfaces/kiosk.ts`**
- Add property: `participant: boolean;` (non-optional, always present via `_all_readable`)

---

## Chapter 1b: Stream Activity Detection ✅ DONE

Decide how to determine whether a stream is currently active (producing data) vs. paused/stalled/offline.

### Decisions Made

#### Part A: Media Element (`backend/elements/media.py`) — Computed `active()` Method

Add two methods following the same pattern as `locked()` on Screen element:

**`active()` method** — computed property, NOT stored in DB:
- Returns `True` for all non-stream types (type != 3)
- Returns `False` for type=3 (Stream) — streams start as "unknown" until background job confirms

**Override of `json()` method:**
```python
def json(self):
    result = super().json()
    result['active'] = self.active()
    return result
```
- Ensures `active` is always included in API responses (like `locked` on Screen)
- Initial value from HTTP GET: `True` for all non-streams, `False` for streams

#### Part B: Background Job (`backend/helpers/stream_health.py`) — NEW FILE

Daemon process using Python's `multiprocessing.Process`, same pattern as existing `challonge.py` and `discord.py`:

| Aspect | Detail |
|--------|--------|
| **File** | New file: `backend/helpers/stream_health.py` |
| **Pattern** | Daemon Process (like `start_challonge_fetcher()` / `start_discord_worker()`) |
| **Interval** | Every 10 seconds |
| **Detection method** | FFprobe with timeout to prevent hangs on broken streams |
| **Scope** | All Media elements where `type=3` (Stream) and `src_type=0` (web URL). S3-stored streams (`src_type=1`) are skipped. |
| **Criteria for "active"** | ffprobe succeeds + stream has no duration (live, actively producing) OR has frames being received. If ffprobe fails/times out → inactive. |

#### Part C: WSS Integration — `transmit_media_health()` Function in `backend/helpers/wss.py`

**Option C1 chosen:** Add a new dedicated function that broadcasts **only the stream health status** (not full media JSON) to all connected clients, avoiding exposure of sensitive attributes like `src`, `user_id`, etc.:

```python
def transmit_media_health(media):
    """Broadcast stream health status (active flag only) to ALL connected clients."""
    result = {'media_id': media['_id'], 'active': media.active(), 'content': 'stream_health'}
    com_rx_queue.put({'what': 'send', 'target': 'all', 'msg': json.dumps(result)})
```

- Called by the background job after each ffprobe check cycle
- **New message type** (`'content': 'stream_health'`) — distinct from regular media updates
- Target is `'all'` so both admin users and participant clients receive updates
- Minimal payload: only `media_id`, `active`, and `content`

#### Part C.5: Media Endpoint Permissions (`backend/endpoints/media.py`)

Add `'active'` to these two lists (so all users can read the computed active status):
| List | Purpose |
|------|---------|
| `_other_readable` | Logged-in non-owner users can read it |
| `_all_readable` | Unauthorized visitors can read it |

#### Part D: Frontend Integration (`frontend/src/app/services/web-socket.service.ts`)

**No changes needed.** The frontend already subscribes to WSS messages via existing handlers (e.g., `ParticipantInterfaceComponent.wssRx()`). The new message type `'stream_health'` is handled by checking for the `content` field and updating local state with `{ media_id, active }`.

The only frontend work needed:
- When a stream health update arrives (`msg['content'] == 'stream_health'`), store `{ media_id → active }` in a Map
- The card UI re-renders reactively based on this updated state

#### Part E: Frontend Display (`participant-interface.component.ts/html`)

Use the stream health data to show visual indicators on stream cards — green dot for active, red for inactive.

### Data Flow Summary
```
HTTP GET /media/ → frontend receives Media with active=False (initial computed state)
    │
    └─► Background job starts (every 10s): ffprobe check all type=3 streams
            │
            └─► transmit_media_health(media) → same format as transmit_media_update but target='all'
                    │
                    └─► Existing frontend WSS handler picks up { 'media': {...}, 'content': 'update' }
                            │
                            └─► Frontend updates local state with new active value from payload
                                    │
                                    └─► Stream cards show green/red dot based on real-time status
```

### Files Affected
| File | Action |
|------|--------|
| `backend/elements/media.py` | Add `_health_registry`, `active()` method + override `json()` |
| `backend/helpers/stream_health.py` | **NEW** — background job with ffprobe checks |
| `backend/main.py` | Start the new stream health process in startup sequence |
| `backend/helpers/wss.py` | Add `transmit_media_health()` function (minimal payload) |
| `backend/endpoints/media.py` | Add `'active'` to `_other_readable` and `_all_readable` |
| `frontend/src/app/interfaces/media.ts` | Add `active: boolean;` property |
| `frontend/src/app/components/participant/...` | Use stream health data for card indicators |

---

## Chapter 2: Frontend — Update Kiosk Interface + Card UI ✅ DONE

Build the kiosk card section and the stream cards section of the ParticipantInterfaceComponent.

### What needs to happen

**Component TS (`participant-interface.component.ts`)**
- Add `CommonModule` import (for Angular `@if` directives)
- Add `participantKiosks` getter — filters kiosks where `participant === true`, sorted alphabetically by name
- Add `activeStreams` getter — filters screens that:
  - Use the `stream-player` template (`template_id == streamScreenTemplateId`)
  - Have an associated Media with `type=3` (Stream) and `active === true` (from WSS health updates, not initial HTTP state)
- Add `openKioskDisplay(name: string)` method — opens `/display?name={name}` in a new tab via `window.open()`
- Add `openStream(screenId: string)` method — placeholder for Chapter 4 viewing strategy implementation

**HTML Template (`participant-interface.component.html`)**
- Dark-themed layout matching the app's existing style (gray-900 background, PrimeNG icons)
- **Header section** with title and description
- **Available Kiosks section** — responsive grid of cards showing:
  - Kiosk name + icon
  - Description text (conditionally shown if present)
  - Status indicator dot (green = active with timeline, gray = idle)
  - External link icon on hover
  - Click opens display in new tab
- Empty state message when no participant kiosks are available
- **Available Streams section** — responsive grid of cards showing:
  - Stream title/description (from Screen `desc` and/or Media `desc`)
  - Active/inactive indicator dot (green = active from WSS health, red = inactive/stale)
  - Click opens stream viewer (strategy TBD in Chapter 4)
- Empty state message when no active streams are available

**Filtering Logic for Streams:**
- Only screens using the `stream-player` template are considered
- The associated Media must have `type=3` and `active === true` (confirmed by background job via WSS)
- Screens whose stream is inactive (`active=false`) are **hidden** from participants (not shown at all)
- This means streams appear in the list only when the background job has confirmed they are actively producing data

**SCSS (`participant-interface.component.scss`)**
- Currently empty. Tailwind utility classes used exclusively — no custom CSS needed unless overrides required.

### Decisions Made for Chapter 2
| Decision | Choice |
|----------|--------|
| Extra card content (timeline name, owner info) | **None** — kiosk cards show only name + description; stream cards show only Screen `desc` |
| Empty state messages | *"No kiosks are currently available for participants."* / *"No active streams available at this time."* |
| Icons | PrimeNG icons already used across the app (`pi-desktop`, `pi-external-link`) — stick with those |
| Stream card content source | Screen `desc` only, NOT Media description |

---

## Chapter 3: Stream Viewing Strategy ⬜ NOT STARTED

Decide how participants view selected streams.

### Options Under Consideration

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A — Inline Modal/Dialog** | Embed `<screen-stream-player>` in a PrimeNG dialog overlay on the participant interface page | Reuses existing `StreamPlayerComponent`; no new route needed; everything in one tab | Modal may feel cramped; videojs player sizing in dialogs can be tricky |
| **B — Dedicated Route** | New lightweight component at `/participant/stream/:screenId`, opens in new tab for fullscreen viewing | Clean dedicated experience; easy fullscreen; reuses `StreamPlayerComponent` inside wrapper | Requires creating a new component; adds another route |
| **C — Hybrid** | Modal shows small thumbnail/preview; "Watch Full" button opens dedicated route in new tab | Best of both worlds | More complex implementation |

---

## Chapter 4: Stream Card Preview ⬜ NOT STARTED

Decide what stream cards display.

### Options Under Consideration

| Option | Description |
|--------|-------------|
| **Text only** | Just the stream title/description (from Screen `desc` and/or Media `desc`) — simplest, no extra API calls |
| **Thumbnail + text** | Show a small preview image extracted from the associated Media element — requires fetching media thumbnail or using first frame of video/stream |

---

## Chapter 5: Implement Stream Cards + WSS Reactive Updates ✅ SUPERSERVED BY CH2+CH3

All functionality from this chapter was implemented in Chapters 2 and 3:
- **Ch2** built the stream cards HTML template with reactive WSS updates (stream health Map, `activeStreams` getter)
- **Ch3** wired `openStream()` to the dedicated route viewer (`/participant/stream/:screenId`)

The data flow diagram below is outdated — everything works end-to-end.

---

## Chapter 6 (Optional): Discoverability Link ⬜ NOT STARTED

Add a subtle link/button on the wildcard display route (`/**`) so visitors can discover and navigate to `/participant`.

### Considerations
- The default fallback route shows `DisplayComponent` when no `name` parameter is provided
- Could add a small "Participant Mode" button/link visible on that page
- Would help LAN party attendees find the interface without knowing the URL

---

## Current Status

| Chapter | Description | Status | Notes |
|---------|-------------|--------|-------|
| **1** | Backend: Add `participant` attribute to Kiosk | ✅ IMPLEMENTED | `kiosk.py` attr + endpoint permissions + frontend interface |
| **1b** | Stream Activity Detection | ✅ FULLY IMPLEMENTED | All backend + frontend done: media element `active()` + `json()` override, stream_health worker daemon, WSS `transmit_media_health()`, endpoint permissions, frontend `streamHealth` Map + WSS handler + `activeStreams` getter. Worker started in `main.py`. |
| **2** | Frontend: Update Kiosk interface + card UI | ✅ IMPLEMENTED | Full template built with kiosk cards grid (name, description, status dot, external link), active streams grid (header/description, pulsing live indicator), empty states, responsive Tailwind layout. Added `participantKiosks` getter, `openKioskDisplay()`, `openStream()` placeholder. |
| **3** | Stream Viewing Strategy (Option B) | ✅ IMPLEMENTED | Dedicated route at `/participant/stream/:screenId`. Added `showControls` input to StreamPlayerComponent (defaulting to false). StreamViewerComponent fetches screen by ID, shows player with controls enabled, handles 404 error state. `openStream()` updated to open new tab. |
| **4** | Stream card preview | 📋 PLANNED | Two options documented (text only vs thumbnail+text) — decision not yet made. Cards currently show text only (Screen header/desc). |
| **5** | Implement stream cards + WSS reactive updates | ✅ SUPERSERVED BY CH2+CH3 | Stream cards HTML built in Ch2; `openStream()` wired to dedicated route in Ch3. Data flow diagram below is outdated — all functionality is implemented. |
| **6** | Optional: Discoverability link from default display | 📋 PLANNED | Idea documented, no implementation started |
---
## Implementation Details

### Chapter 1 — Backend: Add `participant` attribute to Kiosk ✅ FULLY IMPLEMENTED

| File | What was done |
|------|---------------|
| `backend/elements/kiosk.py` | Added `participant=ElementBase.addAttr(type=bool, default=False, notnone=True)` to `_attrdef`; added docstring line |
| `backend/endpoints/kiosk.py` | Added `'participant'` to `_other_readable`, `_all_readable`, `_other_createable`, `_other_updateable` |
| `frontend/src/app/interfaces/kiosk.ts` | Added `participant: boolean;` (non-optional) |

### Chapter 1b — Stream Activity Detection ✅ FULLY IMPLEMENTED

| File | What was done |
|------|---------------|
| `backend/elements/media.py` | Added `_health_registry = {}` class attribute; added `active()` method (returns True for non-streams, checks registry for streams); added `json()` override to include `active` in responses |
| `backend/helpers/stream_health.py` | **NEW FILE** — daemon Process with `_health_checker()`, ffprobe-based detection every 10s, `_update_active_status()` with WSS broadcast |
| `backend/main.py` | Imported and called `start_stream_health_worker()` in startup sequence (line 14 import, line 138 call) |
| `backend/helpers/wss.py` | Added `transmit_media_health(media)` function (minimal payload: media_id, active, content) |
| `backend/endpoints/media.py` | Added `'active'` to `_other_readable` and `_all_readable` |
| `frontend/src/app/interfaces/media.ts` | Added `active: boolean;` property |
| `frontend/.../participant-interface.component.ts` | Added `streamHealth: Map<string, boolean>` state; added WSS handler for `'stream_health'` content type in `wssRx()`; added `activeStreams` getter that filters screens by template + health status

### Chapter 2 — Frontend: Update Kiosk interface + card UI ✅ FULLY IMPLEMENTED

| File | What was done |
|------|---------------|
| `frontend/src/app/components/participant/participant-interface/participant-interface.component.ts` | Added `CommonModule` import; added `participantKiosks` getter (filters by `participant===true`, sorted alphabetically); added `openKioskDisplay()` method (`window.open('/display?name=...')`); added `openStream()` placeholder |
| `frontend/src/app/components/participant/participant-interface/participant-interface.component.html` | Full dark-themed template: header section, kiosk cards grid (name, desc, status dot, external link icon on hover), active streams grid (header/desc, pulsing green live indicator), empty states for both sections. Responsive 1→2→3 col Tailwind grid |
| `frontend/src/app/components/participant/participant-interface/participant-interface.component.scss` | Empty — all styling via Tailwind utility classes

### Chapter 3 — Stream Viewing Strategy (Option B: Dedicated Route) ✅ FULLY IMPLEMENTED

| File | What was done |
|------|---------------|
| `frontend/src/app/components/screens/stream-player/stream-player.component.ts` | Added `showControls = input(false)` input; passed `{ controls: this.showControls() }` to videojs config — allows showing control-bar for participant viewing while keeping display mode hidden |
| `frontend/src/app/components/participant/stream-viewer/stream-viewer.component.ts` | Full implementation: reads `screenId` from route params via `ActivatedRoute`, fetches screen via `ScreenService.getScreen()`, handles 404/error states, imports `StreamPlayerComponent` + `RouterModule` |
| `frontend/src/app/components/participant/stream-viewer/stream-viewer.component.html` | Error state template ("Stream Not Found" + back link) and stream player template with `[showControls]="true"` |
| `frontend/src/app/components/participant/stream-viewer/stream-viewer.component.scss` | Empty — all styling via Tailwind utility classes |
| `frontend/src/app/app.routes.ts` | Added route: `{ path: 'participant/stream/:screenId', component: StreamViewerComponent }` before wildcard |
| `frontend/src/app/components/participant/participant-interface/participant-interface.component.ts` | Updated `openStream()` to call `window.open('/participant/stream/' + screenId, '_blank')` instead of placeholder

---
## Open Questions (from planning phase)

1. **Chapter 4:** Stream card preview style? (text only vs thumbnail+text) — cards currently show text only (Screen header/desc), no extra API calls needed
