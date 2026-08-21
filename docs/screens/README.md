# ScreenTemplates

ScreenTemplates define blueprints for what can be displayed on Kiosks. Each template specifies a set of typed variables that must (or can) be filled in when creating a concrete Screen instance.

## System Templates

The following templates are automatically created on fresh install:

* **[Plain Text](./plain-text.md)** — Displays text with configurable color and size
* **[Background Image](./background-image.md)** — Image Media displayed in background, with optional text overlay
* **[Countdown](./countdown.md)** — Counts down the seconds to a target timestamp
* **[Announcements](./announcements.md)** — Displays announcements from nlpt.online
* **[Player Counts](./player-counts.md)** — Shows player counts from Prometheus and/or Discord sources (available as Multi, Prometheus-only, or Discord-only variants)
* **[TrackMania Stats](./tas.md)** — TrackMania TimeAttackServer wallboard with challenge and global ranks
* **[Video](./video.md)** — Video Media played fullscreen with loop/repeat support
* **[Stream](./stream.md)** — Stream (HLS/DASH) played fullscreen with optional text header overlay
* **[Challonge Round Completion](./challonge-round-completion.md)** — Shows pairs and their completion status for the current round in a Challonge tournament
* **[Challonge Parallel Tournaments](./challonge-parallel-tournaments.md)** — Displays two parallel tournaments side by side with round progress
* **[Jump-to Timeline](./jump-to-timeline.md)** — Switches the Kiosk to a different Timeline (default or specified)

## Variable Types

Each ScreenTemplate defines variables with specific types:

| Type | Description | Example Default |
|------|-------------|-----------------|
| `str` | Short text string | `'some text'` |
| `text` | Rich-text / multiline field | `'line 1\nline 2'` |
| `int` | Integer number | `9` |
| `float` | Decimal number | `3.14` |
| `bool` | Boolean flag | `false` |
| `ts` | Unix timestamp (seconds) | `1697000000` |
| `media` | Any Media element reference | — |
| `media0`–`media3` | Media of specific type (0=image, 1=animated, 2=video, 3=stream) | — |
| `media01` | Media of type 0 or 1 | — |
| `discordguild` | ID of a DiscordGuild element | — |
| `discordrole` | ID of a DiscordRole element | — |
| `tt` | ID of a TimelineTemplate | — |

## Template Attributes

Each ScreenTemplate has the following core attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `key` | str | Unique identifier used by the Frontend to load the corresponding display component (read-only) |
| `name` | str | Human-readable name shown in the admin UI (read-only, unique) |
| `desc` | str | Short description of what this template does (read-only) |
| `endless` | bool | Whether the screen can run indefinitely or has a defined end |
| `duration` | int\|None | Duration in seconds; `null` means unknown or endless |
| `variables_def` | dict | Dictionary defining available variables with their types, defaults, and descriptions |

## Read-Only Attributes

The following attributes are managed by the system and cannot be edited through the UI:
- `key` — determines which frontend component renders the screen
- `name` — unique display name
- `desc` — description
- `endless` — whether the screen has a defined end
- `duration` — screen duration in seconds
- `variables_def` — variable definitions schema

## State Methods

Screens created from these templates have state-checking methods:
- `locked()` — returns True if the Screen is locked (cannot be changed)
- `displayed()` — returns True if the Screen is currently being displayed
- `default()` — returns True if this Screen is member of a default/fallback Timeline
