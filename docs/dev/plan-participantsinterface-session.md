# Participant Interface Implementation Plan

Session started: 2026-08-14

## Session Rules (DO NOT IGNORE)

**NO FILE CHANGES ALLOWED during planning phase.** You are strictly forbidden from modifying any files until the user explicitly gives permission. All work is discussion and planning only — no code changes, no file creation (except this savepoint document itself).

**After loading a saved checkpoint of this document:** Immediately list all chapters with their status and ask the user where to continue. Do not proceed with any chapter until the user selects one.

**When asked to "update the savepoint":** You ARE allowed to modify this file in-place (e.g., mark chapters as done, add new decisions). This is an explicit exception to the no-file-changes rule

**When asked to implement a specific chapter:** You ARE allowed to modify files for that chapter only (component TS/HTML, backend elements/endpoints, etc.). This is an explicit exception to the no-file-changes rule — but ONLY touch files directly related to the requested chapter. Do not modify other chapters' plans, unrelated files, or any content outside the scope of the implementation request.

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

## Chapter 5: Implement Stream Cards + WSS Reactive Updates ⬜ NOT STARTED

Build the stream card section, wire up the chosen viewing strategy (Ch3), and integrate WebSocket updates.

### Data Flow
```
User visits /participant
    │
    ├─► HTTP GET /kiosk/ → filter kiosks with participant=true
    │   └─► Display as kiosk cards
    │       └─► Click → window.open('/display?name={name}')
    │
    ├─► HTTP GET /screen/ → find displayed screens using stream-player template
    │   └─► Cross-reference with participant kiosks (via WSS or client-side join)
    │   └─► Display as stream cards
    │       └─► Click → navigate to chosen viewing strategy route/modal
    │
    └─► WSS admin feed → reactive updates when screens/kiosks change
```

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
| **1b** | Stream Activity Detection | 🟡 PARTIALLY IMPLEMENTED | Backend fully done (media element, stream_health worker, WSS). Frontend `Media.active` property added but card UI not built. Worker not yet started in `main.py`. |
| 2 | Frontend: Update Kiosk interface + card UI | ⬜ NOT STARTED | Component TS skeleton exists with data loading (kiosks, screens, templates, WSS rx). HTML template still has placeholder `<p>participant-interface works!</p>` — no cards rendered. |
| **3** | Stream viewing strategy | 📋 PLANNED | Three options documented (A=modal, B=dedicated route, C=hybrid) — decision not yet made |
| **4** | Stream card preview | 📋 PLANNED | Two options documented (text only vs thumbnail+text) — decision not yet made |
| **5** | Implement stream cards + WSS reactive updates | ⬜ NOT STARTED | Depends on Ch3/Ch4 decisions. Data flow planned in document. |
| 6 | Optional: Discoverability link from default display | 📋 PLANNED | Idea documented, no implementation started |

---
## Implementation Details

### Chapter 1 — Backend: Add `participant` attribute to Kiosk ✅ FULLY IMPLEMENTED

| File | What was done |
|------|---------------|
| `backend/elements/kiosk.py` | Added `participant=ElementBase.addAttr(type=bool, default=False, notnone=True)` to `_attrdef`; added docstring line |
| `backend/endpoints/kiosk.py` | Added `'participant'` to `_other_readable`, `_all_readable`, `_other_createable`, `_other_updateable` |
| `frontend/src/app/interfaces/kiosk.ts` | Added `participant: boolean;` (non-optional) |

### Chapter 1b — Stream Activity Detection 🟡 PARTIALLY IMPLEMENTED

**Backend — ✅ FULLY IMPLEMENTED:**

| File | What was done |
|------|---------------|
| `backend/elements/media.py` | Added `_health_registry = {}` class attribute; added `active()` method (returns True for non-streams, checks registry for streams); **missing**: override of `json()` to include `active` in responses |
| `backend/helpers/stream_health.py` | **NEW FILE** — daemon Process with `_health_checker()`, ffprobe-based detection every 10s, `_update_active_status()` with WSS broadcast |
| `backend/helpers/wss.py` | Added `transmit_media_health(media)` function (minimal payload: media_id, active, content) |
| `backend/endpoints/media.py` | **TODO**: Add `'active'` to `_other_readable` and `_all_readable` |
| `frontend/src/app/interfaces/media.ts` | Added `active: boolean;` property |

**Frontend — ⬜ NOT IMPLEMENTED:**
- No WSS handler for `stream_health` content type yet (only kiosk/screen updates in `wssRx()`)
- No stream health Map/state to store `{ media_id → active }`
- Card UI not built (see Chapter 2)

**Startup — ⬜ NOT IMPLEMENTED:**
- `backend/main.py`: `start_stream_health_worker()` not yet called in startup sequence

### Chapter 2 — Frontend: Update Kiosk interface + card UI ⬜ PARTIALLY STARTED

| File | What was done |
|------|---------------|
| `frontend/src/app/components/participant/participant-interface.component.ts` | Component skeleton exists with: data loading (kiosks, screens, stream template ID), WSS subscription handler for kiosk/screen updates. **Missing**: `participantKiosks` getter, `activeStreams` getter, `openKioskDisplay()`, `openStream()` methods |
| `frontend/src/app/components/participant/participant-interface.component.html` | Still has placeholder `<p>participant-interface works!</p>` — no cards rendered |
| `frontend/src/app/components/participant/participant-interface.component.scss` | Empty (Tailwind-only approach planned) |

---
## Open Questions (from planning phase)

1. **Chapter 3:** Which viewing strategy? (A=modal, B=dedicated route, C=hybrid)
2. **Chapter 4:** Stream card preview style? (text only vs thumbnail+text)
