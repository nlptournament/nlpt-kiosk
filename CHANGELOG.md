# NLPT-Kiosk Changelog

## v1.2.0

### New Features

  * Participant Interface — A new public-facing UI (`/participant`) where LAN party attendees can browse available kiosks and active streams without logging in. Includes a dedicated stream-viewer page (`/participant/stream/:screenId`). Controlled by new `participant_interface` setting, with per-kiosk `participant` flag
  * Timelines can be used like presentations and be actively controlled by Presenter-Interface (see: [docs/presenter-interface.md](docs/presenter-interface.md) for more information)
  * Presentation Wizard to import PDFs as presentation TimelineTemplates, creating all required Media, Screens and TimelineTemplate with one click
  * New *Jump-to Timeline* Screen, that allows automatic Timeline switching on Kiosks (see: [docs/screens/jump-to-timeline.md](docs/screens/jump-to-timeline.md) for more info)

### Fixes/Improvements

  * Video Screen is now capable of looping a video endless or repeat it for a specific amount
  * The duration of video media is now determined to be displayed on Screen element
  * Stream Screens now support styled headers, that are display overlayed on top of the video stream, with configurable positioning and sizing variables
  * Timelines now support a compact display mode in the Presenter interface for better overview during presentations
  * Stream Health Detection — Background worker using ffprobe polls stream URLs every 10 seconds, broadcasting live `active`/`inactive` status via WSS to all connected clients for reactive health indicators

## v1.1.0

### New Features

  * It's now possible to connect a Discord Bot to your server, that fetches the player activity. The counts of the played games can then be displayed on a Kiosk. For more information see: [docs/discord-bot-setup.md](docs/discord-bot-setup.md)
  * Streamer-Interface that focuses on starting and stopping Streams fast (see: [docs/streamer-interface.md](docs/streamer-interface.md) for more information)
  * Stream Wizard to create Media, Screen and TimelineTemplate for URL based Streams in one go
  * Kiosks can now have a default Timeline, with quick (synced) apply options
  * Timelines can now be defined as *single_shot*. They get automatically deleted after been displayed
  * Created tool **GameAbbr** to change the displayed name of incomming game statistics (prometheus & discord) to be displayed on Screens
  * Prometheus endpoint, that can be enabled in Settings. This currently only provides collected data from Discord
  * *User->Profile* dialog to change personal preferences
  * header of Screens can now be customized on per-Screen basis
  * setup guide for debian-trixie based Raspberry Pi OS Kiosks ([KioskPi](docs/install-kiosk-rpi-trixie.md)) - to be able to move away from bookworm-based Raspberry Pi OS

  * Stream ScreenTemplate now supports styled headers with configurable positioning and sizing variables
  * Streams can display overlay text on top of the video stream via the header property
  * Dedicated Presenter-Screen UI for controlling presentations from the Admin-Interface

### Fixes/Improvements

  * direct access to S3 stored media, to reduce processing power on backend
  * Reorganized menu on Admin-Interface
  * Design-tweaks in Admin-Interface on Kiosk representation
  * haproxy got it's own container, to bundle config better to versioning and make it more stable

### Minor Changes

  * moved ansible playbook to setup Raspberry Pi into [nils_ost.nlpt_kiosk](https://github.com/nils-ost/ansible-collection-nlpt_kiosk) collection, see [automated install with ansible](docs/install-with-ansible.md) to get an idea how to use it
  * wrote a bunch of docs to give newcomers at least an idea what NLPT-Kiosk-Controller is about and what one can do with it
