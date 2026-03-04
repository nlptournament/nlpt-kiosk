# NLPT-Kiosk Changelog

## v1.1.0

### New Features

  * It's now possible to connect a Discord Bot to your server, that fetches the player activitiy. The counts of the played games can then be displayed on a Kiosk. For more information see: [docs/discord-playercount.md](docs/discord-playercount.md)
  * Streamer-Interface that focuses on starting and stopping Streams fast (see: [docs/streamer-interface.md](docs/streamer-interface.md) for more information)
  * Stream Wizard to create Media, Screen and TimelineTemplate for URL based Streams in one go
  * Kiosks can now have a default Timeline, with quick (synced) apply options
  * Timelines can now be defined as *single_shot*. They get automatically deleted after been displayed
  * Prometheus endpoint, that can be enabled in Settings. This currently only provides collected data from Discord
  * *User->Profile* dialog to change personal preferences

### Fixes/Improvements

  * Reorganized menu on Admin-Interface
  * Design-tweaks in Admin-Interface on Kiosk representation
