from noapi import ElementBase, docDB


class Timeline(ElementBase):
    """
A Timeline defines what is displayed on a Kiosk. It containes the order of Screens and where to start on the Timeline.

template_id : str | None
    TimelineTemplate a Timeline pulls it's information from.
kiosk_id : str
    Kiosk a Timeline is attached to, but not necessarily displayed at
screen_ids : list
    list of Screens used by this Timeline, this also sets the order of apperance on the Kiosk
start_pos : int (default: 0)
    time index (as seconds) at which Timeline is started, when displayed
current_pos : int (default: 0)
    time index (as seconds) at which Timeline is currently displayed on Kiosk
    If Timeline is not displayed this value equals to start_pos

locked() : bool
    if True, Timeline is not allowed to be changed
    is True if Timeline is currently displayed on a Kiosk
preset() : bool
    is True if Timeline is part of a Preset
    """
    _attrdef = dict(
        template_id=ElementBase.addAttr(type=str, default=None, fk='TimelineTemplate'),
        kiosk_id=ElementBase.addAttr(type=str, notnone=True, fk='Kiosk'),
        screen_ids=ElementBase.addAttr(type=list, default=list(), notnone=True, fk='Screen'),
        start_pos=ElementBase.addAttr(type=int, default=0, notnone=True),
        current_pos=ElementBase.addAttr(type=int, default=0, notnone=True)
    )

    def validate(self):
        errors = dict()
        if self['_id'] is not None and self.locked():
            errors['_id'] = {'code': 70, 'desc': "Timeline can't be changed, as it is locked"}
        if self['start_pos'] < 0:
            errors['start_pos'] = {'code': 7, 'desc': 'needs to be 0 or bigger'}
        if self['current_pos'] < 0:
            errors['current_pos'] = {'code': 7, 'desc': 'needs to be 0 or bigger'}
        return errors

    def save_pre(self):
        if not self.locked():
            self['current_pos'] = self['start_pos']

    def delete_pre(self):
        if self.locked():
            return {'error': {'code': 2, 'desc': "can't be deleted as it is locked"}}

    def locked(self):
        return (docDB.count('Kiosk', {'timeline_id': self['_id']}) > 0)

    def preset(self):
        raise NotImplementedError
