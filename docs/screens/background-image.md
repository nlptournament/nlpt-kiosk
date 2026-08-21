# Screen showing a Background Image

This Screen displays a Media of type *Static Image* or *Animated Image* in fullscreen. Optionally it can display up to two lines of text, overlaying the image.

# specific variables

| Variable   | Type | Default | Description                                                                                         |
| ---------- | ---- | ------- | --------------------------------------------------------------------------------------------------- |
| `image`    | media01 | *(required)* | Media element to be displayed in background; must be type 0 (Static Image) or 1 (Animated Image) |
| `text_above` | str | `''` | Upper line of optional text                                                                         |
| `text_below` | str | `''` | Lower line of optional text                                                                        |
| `text_color` | str | `''` (defaults to `#f0f0f0`) | HTML color of the text lines, e.g. `red`, `#FF0000`. Foreground color is used if not set        |
| `text_space` | int | `0` | Space between the two lines of text; an integer (starting at 0) multiplied by 0.625vw            |
