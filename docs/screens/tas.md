# Screen showing TrackMania Stats (TAS)

This Screen displays a reduced form of the TrackMania TimeAttackServer wallboard. It shows two leaderboards:

1. **Challenge Ranks** — Top players on challenge maps
2. **Global Ranks** — Overall top players across all maps

The screen auto-refreshes every 10 seconds from the TAS server configured in *User → Settings* (`tas_uri`).

> [!NOTE]  
> The TAS endpoint can use mock data if the `mock_tas` setting is enabled in *User → Settings*. When using real data, an internet connection to the TrackMania Stats server is required.

# specific variables

This ScreenTemplate has **no custom variables** — it displays all available challenge and global ranks automatically.

## Display Behavior

- Challenge ranks are limited based on count:
  - ≤ 14 entries → larger display (scale 2)
  - 15–17 entries → medium display (scale 1)
  - > 17 entries → compact display (scale 0)
- Global ranks follow the same scaling logic
- The screen runs indefinitely (`endless: true`) with no defined duration
