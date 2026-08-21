# Screen showing Announcements from nlpt.online

This Screen displays announcements fetched from the [nlpt.online](https://nlpt.online) API. It shows a list of upcoming and current events with their target times, images (if available), and descriptions.

The screen auto-refreshes:
- **Announcements** are re-fetched every 10 seconds from the nlpt.online API
- **Display timing** is updated every second to show countdowns in `HH:MM:SS` format

> [!NOTE]  
> The Announcements endpoint can use mock data if the `mock_anno` setting is enabled in *User → Settings*. When using real data, an internet connection to nlpt.online is required.

# specific variables

This ScreenTemplate has **no custom variables** — it displays all announcements from the configured source automatically.

## Display Behavior

- Announcements with a `target` timestamp show a countdown (e.g., `02:15:30`) or "jetzt" if the time has passed
- If an announcement includes an image (`img` field), it is fetched and displayed alongside the text
- The screen runs indefinitely (`endless: true`) with no defined duration
