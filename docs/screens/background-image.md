# Scrren showing a Background Image

This Screen shows a Media of type *Static Image* or *Animated Image* in fullscreen. Optionally it can display up to two lines of text, overlaying the image.

# specific variables

| variable   | description                                                                                         |
| ---------- | --------------------------------------------------------------------------------------------------- |
| image      | (required) select Media of type *Static Image* or *Animated Image*                                  |
| text_above | first line of optional text                                                                         |
| text_below | second line of optional text                                                                        |
| text_color | give the text some color (default `#f0f0f0`) Takes valied HTML color input e.g. `red` or `#FF0000`  |
| text_space | space between the two lines of text. takes an integer (starting at 0) that is multiplied by 0.625vw |
