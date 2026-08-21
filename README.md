# NLPT-Kiosk(-Controller)

## The Goal

Having a single interface to remote controll a bunch of kiosks (projectors) to display variing information in sync during LAN-Partys (it's not limited to LAN-Partys but the provided Screens are focused to be used on those)

Some of the features are: Looping over different statistics (played games count, gameserver usage) and announcements (NLPT specific) during the the event.
But also ad-hoc information, videos, streams or static/animated pictures during presentations or the night-break.

## The Architecture

### Hardware

First you need to have a KioskController, this should be installed on some kind of (Linux) server, that is always available during an Event.
It permanently communicates with the Kiosk(-Clients), backends to collect data and provides the userinterface to configure the system and what is displayed.

Second you need to have at least one (but as many as you like) Kiosk(-Clients) these are hooked up to a projector or tv and show the information the controller sends them.
This project is designed to use RaspberryPi as Kiosks but every client that is able to show a WebPage in fullscreen is possible to use, but the setup guide
for those is more generic and you might have to tinker around to get everything working as expected.

Setup Guides:

  * [KioskController](docs/install-controller.md)
  * [KioskPi](docs/install-kiosk-rpi-trixie.md)
  * [generic Kiosk-Client](docs/install-kiosk-generic.md)
  * [automated install with ansible](docs/install-with-ansible.md)

### Controller configuration

The system uses a lot of different elements but for the general usage only five do really matter:

  * Kiosk
  * Timeline
  * TimelineTemplate
  * Screen
  * Media

The **Kiosk** is the representation of a Kiosk(-Client) displaying information from the system. It does have one active Timeline (also refered as displayed)
and might have a bunch of *other Timelines* ready to be activated at any time and replacing the currently active Timeline to be displayed.

**Timelines** are always linked to a Kiosk, they can't exist without them, and are just an instance of a TimelineTemplate for a specific Kiosk.
They hold information like the current position in the rotation or where the rotation should start for this Kiosk when the Timeline gets activated.

As mentioned **TimelineTemplates** are the basis for Timelines, they contain the information which Screen(s) should be displayed on the Kiosk and in which order.

**Screens** are the definition of what is displayed. These are the elements that refer to different sources of information and bind them together in a pleasent way to be displayed.
There are a lot of different ScreenTemplates for variing use-cases on what and how to display information (see below for a list of all options)

To be more flexible from where Screens get their information **Media** elements are the way to got. A Media can be a video, pricture, animation or stream.
The Media element ties together what kind of Media it is and where to get it (e.g. the internal S3 storage or a generic web URL)

As an startpoint you can do the [basics tutorial](docs/first-steps.md) to get used to the functions of KioskController.

## The Screen(Templates)

As mentioned above Screens are the representation of WHAT is displayed from WHERE and HOW, to cover the different use-cases the following ScreenTemplates are available:

  * **[Plain Text](docs/screens/plain-text.md)** — Displays text with configurable color and size
  * **[Background Image](docs/screens/background-image.md)** — Image Media in background with optional text overlay
  * **[Countdown](docs/screens/countdown.md)** — Counts down the seconds to a target timestamp
  * **[Announcements](docs/screens/announcements.md)** — Displays announcements from nlpt.online
  * **[Player Counts](docs/screens/player-counts.md)** — Shows player counts from Prometheus and/or Discord sources (Multi, Prometheus-only, or Discord-only variants)
  * **[TrackMania Stats](docs/screens/tas.md)** — TrackMania TimeAttackServer wallboard with challenge and global ranks
  * **[Video](docs/screens/video.md)** — Video Media played fullscreen with loop/repeat support
  * **[Stream](docs/screens/stream.md)** — Stream (HLS/DASH) played fullscreen with optional text header overlay
  * **[Challonge Round Completion](docs/screens/challonge-round-completion.md)** — Shows pairs and their completion status for the current round in a Challonge tournament
  * **[Challonge Parallel Tournaments](docs/screens/challonge-parallel-tournaments.md)** — Displays two parallel tournaments side by side with round progress
  * **[Jump-to Timeline](docs/screens/jump-to-timeline.md)** — Switches the Kiosk to a different Timeline (default or specified)

## The User-Interfaces

  * [Admin-Interface](docs/first-steps.md)
  * [Streamer-Interface](docs/streamer-interface.md)
  * [Presenter-Interface](docs/presenter-interface.md)
  * [Participant-Interface](docs/participant-interface.md)
