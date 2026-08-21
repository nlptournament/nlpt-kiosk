# Screen showing a Countdown

This Screen displays a countdown to a specific point in time. It shows hours, minutes and seconds counting down (format `HH:MM:SS`). Optionally one line of text can be displayed above and/or below the countdown.

A countdown is single-use by nature — when the target time is reached, the screen signals an end event to advance to the next Screen in the Timeline. If a Timeline activates a countdown whose target time has already passed, the end event fires immediately.

# specific variables

| Variable   | Type | Default | Description                                 |
| ---------- | ---- | ------- | ------------------------------------------- |
| `time`     | ts   | *(required)* | Unix timestamp of the target time the countdown ticks towards |
| `text_above` | str | `''` | Optional line of text displayed above the countdown |
| `text_below` | str | `''` | Optional line of text displayed below the countdown |
