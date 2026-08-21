# Screen showing Plain Text

As the name suggests, this screen is meant to just show some text on a black background.

# specific variables

| Variable   | Type | Default | Description                                                                                        |
| ---------- | ---- | ------- | -------------------------------------------------------------------------------------------------- |
| `text`     | text | *(required)* | The text to be displayed; can contain newlines for multiline content                               |
| `text_color` | str | `''` (defaults to `#f0f0f0`) | HTML color of the text, e.g. `red`, `#FF0000`, `blue`. Foreground color is used if not set        |
| `text_size`  | int | `9` | Scale of the text size, values from 1 to 14                                                      |

## Text Size Mapping

| Value | Text Size | Line Height |
| ----- | --------- | ----------- |
| 1     | 0.625vw   | 0.938vw     |
| 2     | 0.938vw   | 1.250vw     |
| 3     | 1.172vw   | 1.406vw     |
| 4     | 1.406vw   | 1.563vw     |
| 5     | 1.875vw   | 1.875vw     |
| 6     | 2.344vw   | 2.344vw     |
| 7     | 2.813vw   | 2.813vw     |
| 8     | 3.750vw   | 3.750vw     |
| 9     | 5.000vw   | 5.000vw     |
| 10    | 6.875vw   | 6.875vw     |
| 11    | 8.750vw   | 8.750vw     |
| 12    | 10.625vw  | 10.625vw    |
| 13    | 12.500vw  | 12.500vw    |
| 14    | 14.375vw  | 14.375vw    |
