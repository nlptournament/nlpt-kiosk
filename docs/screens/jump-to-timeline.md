# Screen for Jumping Between Timelines

When activated, this Screen switches the active Timeline of the calling Kiosk either to the Kiosk's default Timeline or to a predefined TimelineTemplate.

This is useful for scheduled events — e.g., switching all kiosks from a loop of promotional content to a tournament-specific timeline at a specific time.

# specific variables

| Variable    | Type | Default | Description                                                                             |
| ----------- | ---- | ------- | --------------------------------------------------------------------------------------- |
| `use_default` | bool | `false` | If True, the Kiosk's default Timeline is used as the jump target                       |
| `timeline`  | tt   | `''` | ID of a TimelineTemplate to use as jump target; only considered if *use_default* is False |

## How It Works

The `timeline` variable holds an ID of a **TimelineTemplate** (not a Timeline instance). When a jump-to Screen is activated and references a TimelineTemplate:

1. A single-shot Timeline is created from the referenced Template
2. The new Timeline is activated on the Kiosk that displays this Screen
3. This ensures the jump-to Screen works correctly across multiple Kiosks simultaneously

## Stall Behavior

The jump-to Screen can be "stalled" — the corresponding Kiosk shows a black screen in any of these configurations:

- `use_default` is True but the Kiosk does **not** have a default Timeline defined
- `use_default` is False, and the `timeline` variable is empty or contains an invalid TimelineTemplate ID
