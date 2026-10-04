# Screen showing Announcements from nlpt.online and Discord Polls

This Screen displays announcements fetched from the [nlpt.online](https://nlpt.online) API **and/or** Discord polls. It shows a list of upcoming and current events with their target times, images (if available), and descriptions. For Discord polls, it displays poll questions, options, and active countdown timers.

The screen auto-refreshes:
- **Announcements** are re-fetched every 10 seconds from the nlpt.online API (when `src_nlpt` is enabled)
- **Discord Polls** are re-fetched every 10 seconds from Discord (when `src_discordpolls` is enabled)
- **Display timing** (countdowns) is updated every second to show remaining time in `HH:MM:SS` format

> [!NOTE]  
> The Announcements endpoint can use mock data if the `mock_anno` setting is enabled in *User → Settings*. When using real data, an internet connection to nlpt.online is required. Discord polls require a configured Discord bot with poll support (or used mock data if `mock_discord` is enabled).

# specific variables

This ScreenTemplate supports **7 custom variables** for fine-grained control:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `src_nlpt` | boolean | `true` | Fetch announcements from nlpt.online API |
| `src_discordpolls` | boolean | `false` | Fetch and display Discord polls |
| `type_default` | boolean | `true` | Show announcements with `default` layout |
| `type_danger` | boolean | `true` | Show announcements with `danger` layout (highlighted) |
| `type_ffa` | boolean | `true` | Show announcements with `ffa` layout |
| `discord_guild` | string | `''` | Discord guild ID to filter polls from |
| `discord_channels` | array of strings | `[]` | Discord channel IDs to poll for active polls |

## Display Behavior

### Announcements (nlpt.online)
- Three layout types: **default**, **danger** (highlighted), and **ffa** — each with distinct background styling via CSS classes (`bg-anno-default`, `bg-anno-danger`, `bg-anno-ffa`)
- The `danger` layout is displayed first, followed by all other layouts
- Announcements with a `target` timestamp show a countdown (e.g., `02:15:30`) or "jetzt" if the time has passed
- If an announcement includes an image (`img` field), it is fetched from S3 and displayed on the right side (occupying 1/4 of the row width)
- The screen runs indefinitely (`endless: true`) with no defined duration

### Discord Polls
- Displays poll **question**, **options** (in a flex row, each taking 1/4 width), and an active countdown timer showing "läuft noch:" (still running:)
- Shows a Discord poll icon on the left side (occupying 1/5 of the row width)
- Polls are filtered by `active` status — expired polls (where `till_ts` has passed) are hidden
- Styled with CSS class `bg-anno-poll`

### Header
- The screen title defaults to "Ankündigungen" but can be customized via the `header` template variable. If `header` is empty, the default is used.
