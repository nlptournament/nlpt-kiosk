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

    def save_post(self):
        from helpers.wss import transmit_preset_update, transmit_timeline_update
        from elements import Timeline
        transmit_preset_update(self)
        for tl in [Timeline.get(tl) for tl in self['timeline_ids']]:
            transmit_timeline_update(tl)

    def delete_post(self):
        from helpers.wss import transmit_preset_delete
        from elements import Timeline
        for t in [Timeline.get(t) for t in self['timeline_ids']]:
            t.delete()
        transmit_preset_delete(self)

    def apply(self):
        from elements import Timeline
        result = list()
        for t in [Timeline.get(t) for t in self['timeline_ids']]:
            tnew = Timeline(t.json())
            tnew['_id'] = None
            r = tnew.save()
            if 'created' in r:
                result.append(r['created'])
        return result
