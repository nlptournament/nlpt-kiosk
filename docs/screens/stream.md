# Screen showing a Stream

This Screen displays a live Video-Stream in fullscreen mode using the video.js player with HLS/DASH support. It will never issue an end-signal automatically — you must work with the Screen's *Duration* or *Till* attributes, or change the Timeline manually to stop it.

The screen supports **text header overlay** on top of the stream using the `videojs-overlay` plugin. The header text is provided via the shared `header` input (configured in the Screen instance), and its position/size are controlled by template variables.

This Screen works with any Media element of type *Stream* that has a valid **HLS URL** or **DASH URL** as its generic web URL (*internal S3 storage will not work for obvious reasons*). For NLPT, we built our own local streaming server ([nlpt-rtmp-server](https://github.com/nlptournament/nlpt-rtmp-server)) that is fully compatible with this Screen — it accepts OBS capture streams and makes them available on Kiosks.

For this Screen to work properly, the browser on Kiosks needs certain safety measures disabled:
- Auto-playback of videos must be allowed (otherwise the Screen gets stuck)
- CORS should be disabled in the browser (otherwise the Kiosk may not read the stream if the server doesn't send sufficient CORS headers)

See [generic Kiosk-Client](../install-kiosk-generic.md) for Chromium configuration details.

> [!NOTE]  
> If you are using Raspberry Pis for the Kiosks and followed the setup guide ([KioskPi](../install-kiosk-rpi-trixie.md)), the required settings are already applied.

# specific variables

| Variable | Type | Default | Description                  |
| -------- | ---- | ------- | ---------------------------- |
| `stream` | media3 | *(required)* | Media element of type Stream to be played |
| `header_pos` | str | `'top-left'` | Position of the header overlay. Options: `top-left`, `top-center`, `top-right`, `bottom-left`, `bottom-center`, `bottom-right` |
| `header_size` | int | `4` | Relative size of the overlayed header (values 1–7 allowed; mapped to Tailwind text sizes) |

## Header Overlay

The header text is provided via the Screen's `header` variable (shared across all screen types). The position and size are controlled by the template variables above:

- **Position** (`header_pos`) — maps to CSS classes, e.g. `top-left` → `top-0 text-left`
- **Size** (`header_size`) — maps to Tailwind text sizes, e.g. value 4 → `text-7xl` (offset by +3)

## Stream Wizard

The Admin-Interface includes a *Stream Wizard* that streamlines the setup of streams. Instead of manually creating Media, Screen, and TimelineTemplate elements for each stream, just provide the stream URL and which user owns it — all required elements are created automatically. This wizard was introduced alongside the [Streamer-Interface](../streamer-interface.md).
