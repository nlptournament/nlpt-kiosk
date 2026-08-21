# Screen showing a Video

This Screen displays a video in fullscreen mode. After the video finishes, it signals its end and activates the next Screen in the Timeline. The screen supports **loop** (repeat the same video continuously) and **repeat** (play the video N additional times before advancing).

For this Screen to work properly, the browser on Kiosks needs certain safety measures disabled:
- Auto-playback of videos must be allowed (otherwise the Screen gets stuck)
- If your Video Media element uses *generic web URL* as storage, CORS should be disabled in the browser (otherwise the Kiosk may not read the video file if the server doesn't send sufficient CORS headers)

See [generic Kiosk-Client](../install-kiosk-generic.md) for Chromium configuration details.

> [!NOTE]  
> If you are using Raspberry Pis for the Kiosks and followed the setup guide ([KioskPi](../install-kiosk-rpi-trixie.md)), the required settings are already applied.

# specific variables

| Variable | Type | Default | Description                 |
| -------- | ---- | ------- | --------------------------- |
| `video`  | media2 | *(required)* | Media element of type Video to be played |

## Loop and Repeat

The screen supports two repetition modes controlled by the Screen instance (not the template):
- **Loop** — the video plays continuously without end
- **Repeat** — the video plays once, then N additional times before signaling completion and advancing to the next Screen
