from noapi import ElementBase


class Preset(ElementBase):
    """
Save a set of Timelines to reapply them fast to Kiosks

desc : str
    Some useful description for a Preset
timeline_ids : list
    list of timeline_ids a Preset contains (those are duplicated when a Preset is applied)
user_id : str
    creator/owner of the Preset
common : bool (default: False)
    if True Preset is available to all Users, if False only available to owner and admins

apply() : None
    copies all Timelines linked in Preset, to apply them to their corresponding Kiosks
    """
    _attrdef = dict(
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        timeline_ids=ElementBase.addAttr(type=list, default=list(), notnone=True, fk='Timeline'),
        user_id=ElementBase.addAttr(type=str, notnone=True, fk='User'),
        common=ElementBase.addAttr(type=bool, default=False, notnone=True)
    )

    def apply(self):
        from elements import Timeline
        for t in [Timeline.get(t) for t in self['timeline_ids']]:
            tnew = Timeline(t.json())
            tnew['_id'] = None
            tnew.save()
