# Screen showing Challonge Parallel Tournaments

This Screen displays two Challonge tournaments side by side, showing the progress of the current round in each. It is designed for LAN parties running parallel tournament brackets (e.g., Group A vs Group B).

The screen listens for real-time updates via WebSocket when Challonge tournaments or matches are modified through the admin interface.

# specific variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | str | `''` | Optional title to show on top of the Screen |
| `tournament1_id` | int | *(required)* | ID of the first Challonge tournament to display |
| `tournament2_id` | int | *(required)* | ID of the second Challonge tournament to display |
| `signal_completed` | bool | `false` | If enabled, the Screen signals finished when the same (latest, primary) rounds on both tournaments are completed |

## Display Behavior

- Fetches data from the Challonge API for both tournaments simultaneously
- Displays matches with participant portraits and winner tracking for each tournament
- Real-time updates via WebSocket when:
  - Either tournament state changes (pending → underway → complete)
  - Match results are updated in either tournament
  - Participants are modified
- If `signal_completed` is True, the screen emits a finish event when both tournaments have completed their latest primary round

> [!NOTE]  
> Challonge data is cached and refreshed every 10 seconds by a background daemon process. Tournament states: 0=unknown, 1=pending, 2=underway, 3=complete. Match states: 0=unknown, 1=pending, 2=open, 3=complete.
