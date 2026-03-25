# Screen showing a Stream

This Screen displays a Video-Stream in full-screen mode. It will never issue a end-signal, you have to work with the Screens *Duration* or *Till* attributes, or just change the Timeline by hand.

In general this Screen is able to work with every Media alement of type Stream, that has valid *HLS-URL* or *DASH-URL* configured as it's *generic web URL* (*internal S3 storage* will not work for obvious reasons). But for NLPT we built our own local streaming-server (that is fully compatiple with this Screen), to be able to send OBS capture streams to this local server and show them on Kiosks, take a look at [nlpt-rtmp-server](https://github.com/nlptournament/nlpt-rtmp-server) if you are interested in a similar setup.

For this Screen to be utalized, the browser of Kiosks needs to have some safety measures been disabled. At least auto-playback of videos have to be allowed, otherwise the Screen gets stuck. Also CORS should to be disabled in the browser, otherwise the Kiosk might not able to read the stream, if the corresponding server does not send sufficient CORS data itself. For more information on how to achieve this, see the section about Chromium in [generic Kiosk-Client](../install-kiosk-generic.md).

> [!NOTE]
> if you are using Raspberry Pis for the Kiosks, and followed the setup guide in this Dokumentation ([KioskPi](../install-kiosk-rpi-trixie.md)), the required settings are already made.

# specific variables

| variable | description                  |
| -------- | ---------------------------- |
| stream   | Media element of type stream |

# Stream Wizard

To ease things a bit up, regarding steam setup, the Admin-Interface has the *Stream Wizard*. This came to live, when implementing the [Streamer-Interface](../streamer-interface.md), as it was quiet annoying to set up a Media, Screen and TimelineTemplate element for each stream. The *Stream Wizard* steamlines this, just give it the information about the stream-URL and which user owns the stream, and all requiered elements are created for you. Just give it a try ;)
