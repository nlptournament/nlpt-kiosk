# Screen showing a Video

This Screen displays a Video in full-screen mode. After the video finished the Screen signals it's end and the next Screen in Timeline is activated.

For this Screen to be utalized, the browser of Kiosks needs to have some safety measures been disabled. At least auto-playback of videos have to be allowed, otherwise the Screen gets stuck. And if your video Media element has *generic web URL* as Storage, CORS have to be disabled in the browser, otherwise the Kiosk might not able to read the video-file. For more information on how to achieve this, see the section about Chromium in [generic Kiosk-Client](../install-kiosk-generic.md).

> [!NOTE]
> if you are using Raspberry Pis for the Kiosks, and followed the setup guide in this Dokumentation ([KioskPi](../install-kiosk-rpi-trixie.md)), the required settings are already made.

# specific variables

| variable | description                 |
| -------- | --------------------------- |
| video    | Media element of type video |
