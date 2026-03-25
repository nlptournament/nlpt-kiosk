# Screen showing a Countdown

This Screen displays a countdown to a specific point in time. It only shows hours, minutes and seconds counting down. Optionally one line auf text can be displayed above and/or below the countdown.

Be aware, that a countdown is kind of single-use. If the target time is reached, the Screen is signaling a screen-end event to the Controller, for the next Screen in Timeline to be loaded. If a Timeline is activating a countdown Screen, whose target time is already in the past, the screen-end event is send immediately.

# specific variables

| variable   | description                                 |
| ---------- | ------------------------------------------- |
| text_above | optional line of text above the countdown   |
| text_below | optional line of text below the countdown   |
| time       | point in time the countdown "ticks" towards |
