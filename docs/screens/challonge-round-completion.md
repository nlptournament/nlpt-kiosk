# Screen showing Challonge Round Completion

This Screen displays the progress of the current round in a single Challonge tournament. It shows all matches with their participants, results, and completion status.

The screen listens for real-time updates via WebSocket when Challonge tournaments or matches are modified through the admin interface.

# specific variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | str | `''` | Optional title to show on top of the Screen; otherwise the tournament name is displayed |
| `tournament_id` | int | *(required)* | ID of the Challonge tournament to display |
| `signal_completed` | bool | `false` | If enabled, the completion of a (primary) round signals the screen as finished, advancing to the next Screen in the Timeline |

## Display Behavior

- Fetches tournament data from the Challonge API (or mock data if `mock_chal` is enabled)
- Displays matches with participant portraits and winner tracking
- Real-time updates via WebSocket when:
  - Tournament state changes (pending → underway → complete)
  - Match results are updated
  - Participants are modified
- If `signal_completed` is True, the screen emits a finish event when the latest primary round on both sides of the bracket is completed

> [!NOTE]  
> Challonge data is cached and refreshed every 10 seconds by a background daemon process. Tournament states: 0=unknown, 1=pending, 2=underway, 3=complete. Match states: 0=unknown, 1=pending, 2=open, 3=complete.
