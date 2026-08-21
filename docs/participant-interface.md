# Participant Interface

The **Participant Interface** is a public-facing UI that allows LAN party attendees to browse available kiosks and live streams without needing to log in or have any credentials. It provides an at-a-glance view of all active displays and stream health status, with the ability to open dedicated stream viewer tabs for individual screens.

## Overview

| Feature | Description |
|---------|-------------|
| **URL** | `/participant` (browse view) |
| **Stream Viewer** | `/participant/stream/:screenId` (opens in new tab) |
| **Authentication** | None required — fully public |
| **Real-time Updates** | Stream health status via WebSocket (WSS) |

When enabled, the interface shows two sections:

1. **Available Kiosks** — grid of kiosk cards with status indicators and external link icons
2. **Active Streams** — grid of stream-based screens with pulsing green "live" indicators based on real-time health detection

## Enabling the Feature

### Step 1: Enable in Settings

In the admin panel, go to **Settings** and set `participant_interface` to `true`. This single toggle enables the entire feature.

When enabled:
- The `/participant` route becomes accessible
- A "Participant Interface" shortcut appears in the admin menubar
- Kiosks with `participant: true` will be listed on the browse page

### Step 2: Mark Kiosks as Participant-Visible

For a kiosk to appear on the participant interface, it must have its **participant** flag set to `true`. This is configured per-kiosk in the admin panel under the kiosk settings.

Kiosks with `participant: false` (the default) remain hidden from public view but continue operating normally for their intended display purpose.

## What Users See

### Browse View (`/participant`)

The browse page displays two distinct sections:

#### Available Kiosks
- **Grid layout** of kiosk cards showing each kiosk's name and description
- **Status dots** indicating whether the kiosk is currently locked, displaying content, or on default
- **External link icons** — clicking opens the kiosk's display view in a new browser tab

#### Active Streams
- **Grid layout** of stream-based screens (using `stream-player` template)
- **Pulsing green "live" indicators** for streams that are actively producing data
- **Grayed-out indicators** for inactive/broken streams
- Clicking a stream card opens the dedicated stream viewer in a new tab

### Stream Viewer (`/participant/stream/:screenId`)

The stream viewer provides a full-page video player with:

- **Video controls enabled** — play/pause, volume, fullscreen (unlike the display mode which is hidden)
- **Text header overlay** — if configured via screen template variables (`header`, `header_pos`, `header_size`), an overlayed text appears on top of the stream
- **Responsive sizing** — player adapts to browser window dimensions

## Stream Health Detection

The system uses a background worker (`stream_health.py`) to continuously monitor the health of all web URL streams (type=3, src_type=0).

### How It Works

1. Every **10 seconds**, the worker polls all registered stream media elements
2. For each stream, it runs `ffprobe` against the stream URL with a **5-second timeout**
3. If ffprobe successfully retrieves format information with `nb_streams > 0`, the stream is marked as **active**; otherwise **inactive**
4. The health status is broadcast to all connected clients via WebSocket (`stream_health` content type)
5. The participant interface reacts in real-time, updating the pulsing indicators

### Health Check Logic

```
Stream URL → ffprobe (timeout: 5s) → nb_streams > 0?
    ├─ Yes → active = true  → green pulsing indicator
    └─ No  → active = false → gray static indicator
```

The health check only runs when `participant_interface` is enabled in settings. It only checks streams with:
- **type** = 3 (stream)
- **src_type** = 0 (web URL, not S3 stored)

## Technical Details

### Routing

```typescript
{ path: 'participant', component: ParticipantInterfaceComponent },
{ path: 'participant/stream/:screenId', component: StreamViewerComponent }
```

The wildcard route `/**` falls back to the display view, so unknown paths do not produce errors.

### Auto-Redirect

If a user navigates to `/participant` but the `participant_interface` setting is disabled, they are automatically redirected to `/admin`. This ensures the feature cannot be accessed when it has been turned off by an administrator.

### WebSocket Integration

The participant interface subscribes to real-time updates via `WebSocketService`:
- **Stream health updates** — `{media_id, active}` payloads update the health Map reactively
- **Screen changes** — any screen state change triggers a refresh of the displayed content
- **Kiosk updates** — kiosk status changes (lock/unlock) are reflected immediately

### No Authentication

The participant interface does not require login. All data served is:
- Kiosks with `participant: true` flag
- Screen templates and their public variables
- Stream health status (non-sensitive operational data)

No user credentials, internal settings, or private resources are exposed through this interface.

## Admin Menubar Shortcut

When `participant_interface` is enabled, a "Participant Interface" link appears in the admin menubar for quick access during setup and testing. This allows administrators to preview exactly what LAN party attendees will see.
