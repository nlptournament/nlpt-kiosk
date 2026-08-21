# Screen showing Player Counts

This Screen displays the number of players currently active across different games. It supports two data sources:

- **Prometheus** — queries game server metrics via a Prometheus endpoint (configured in *User → Settings*)
- **Discord** — counts members playing the same game within a Discord guild (requires [Discord Bot Setup](../discord-bot-setup.md))

## Available Variants

Three ScreenTemplate variants are available, all sharing the `player-counts` key:

### Player Counts - Multi

The most flexible variant. Allows enabling both Prometheus and Discord sources simultaneously, with optional filtering by Discord guild and role.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `src_prom` | bool | `false` | Enable Prometheus source for this Screen |
| `src_discord` | bool | `false` | Enable Discord source for this Screen |
| `guild` | discordguild | `''` | Only members of this guild are counted (Discord) |
| `role` | discordrole | `''` | Only members with this role are counted (Discord) |

### Player Counts - Prometheus

Optimized for Prometheus-only displays. The source flag is read-only and always enabled.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `src_prom` | bool | `true` | Prometheus Source is enabled (read-only) |

### Player Counts - Discord

Optimized for Discord-only displays. The source flag is read-only and always enabled.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `guild` | discordguild | `''` | Only members of this guild are counted |
| `role` | discordrole | `''` | Only members with this role are counted |
| `src_discord` | bool | `true` | Discord Source is enabled (read-only) |

## Display Behavior

- **Prometheus data** refreshes every 8 seconds
- **Discord data** refreshes every 3 seconds
- When both sources are active, Prometheus results are limited to the top 12 games by activity
- The screen auto-scales content size based on the number of items displayed:
  - ≤ 4 items → larger display
  - 5–9 items → medium display
  - > 9 items → compact display

> [!NOTE]  
> When using Discord filters, select a guild first — the available roles are requested from the backend based on the selected guild. For Discord bot setup instructions, see [Discord Bot Setup](../discord-bot-setup.md).
