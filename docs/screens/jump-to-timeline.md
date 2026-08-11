# Screen for jumping between Timelines

Screen, when activated, switches the active Timeline of calling Kiosk either to the default Timeline of Kiosk or a predifined Timeline.

# specific variables

| variable    | description                                                                             |
| ----------- | --------------------------------------------------------------------------------------- |
| use_default | if True the default Timeline is used as jump-target                                     |
| timeline    | id of a TimelineTemplate used as jump-target, only considered if *use_default* is False |

# technical information

The variable *timeline* is meant to hold an id of a TimelineTemplate. When a jump-to Screen is activated, that references a TimelineTemplate, a single-shot Timeline is created from this Template, and activated on the Kiosk calling the jump-to Screen. This ensures, that a jump-to Screen is usable on multiple Kiosks.

It is possible to stall a jump-to Screen, the corresponding Kiosk just show a black Screen if one of the following configuration combinations exists:

  * the Screen has *use_default* set to True but the Kiosk dows not have a default Timelne defined
  * the Screen has *use_default* set to False, but also the variable *timeline* is empty or has an invalid TimelineTemplate id configured
