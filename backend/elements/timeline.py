from noapiframe import ElementBase, docDB
import time


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
start_time : int | None (default: None)
    time, as timestamp, when this Timeline should start to run on Kiosk, needs to be in the future
    this value is used for synced starts of Timelines on multiple Kiosks
single_shot : bool & notnull
    If set to True, Timeline gets deleted after it's been displayed on a Kiosk

locked() : bool
    if True, Timeline is not allowed to be changed
    is True if Timeline is currently displayed on a common Kiosk
displayed() : bool
    if True, Timeline is not allowed to be deleted
    is True if Timeline is currently displayed on a Kiosk
default() : bool
    if True, Timeline is not allowed to be deleted
    is True if Timeline is default of a Kiosk
preset() : bool
    is True if Timeline is part of a Preset
    """
    _attrdef = dict(
        template_id=ElementBase.addAttr(type=str, default=None, fk='TimelineTemplate'),
        kiosk_id=ElementBase.addAttr(type=str, notnone=True, fk='Kiosk'),
        screen_ids=ElementBase.addAttr(type=list, default=list(), notnone=True, fk='Screen'),
        start_pos=ElementBase.addAttr(type=int, default=0, notnone=True),
        current_pos=ElementBase.addAttr(type=int, default=0, notnone=True),
        start_time=ElementBase.addAttr(type=int, default=None),
        single_shot=ElementBase.addAttr(type=bool, default=False, notnone=True)
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
        if not self.displayed():
            self['current_pos'] = self['start_pos'] * 2
        self['start_pos'] = int(int(self['start_pos']) % len(self['screen_ids']))
        self['current_pos'] = int(int(self['current_pos']) % (len(self['screen_ids']) * 2))
        if self['start_time'] is not None:
            if time.time() > self['start_time']:
                self['start_time'] = None

    def save_post(self):
        from helpers.wss import transmit_timeline_update, transmit_screen_update
        from elements import Screen
        for s in [Screen.get(s) for s in self['screen_ids']]:
            transmit_screen_update(s)
        transmit_timeline_update(self)

    def delete_pre(self):
        if self.displayed() or self.default():
            return {'error': {'code': 2, 'desc': "can't be deleted as it is locked"}}

    def delete_post(self):
        from elements import Preset
        from helpers.wss import transmit_timeline_delete
        for p in [Preset(p) for p in docDB.search_many('Preset', {'template_ids': self['_id']})]:
            p['template_ids'].remove(self['_id'])
            p.save()
        transmit_timeline_delete(self)

    def locked(self):
        from elements import Kiosk
        return (Kiosk.count({'timeline_id': self['_id'], 'common': True}) > 0)

    def displayed(self):
        from elements import Kiosk
        return (Kiosk.count({'timeline_id': self['_id']}) > 0)

    def default(self):
        from elements import Kiosk
        return (Kiosk.count({'default_timeline_id': self['_id']}) > 0)

    def preset(self):
        from elements import Preset
        return (Preset.count({'timeline_ids': self['_id']}) > 0)

    def json(self):
        result = super().json()
        result['locked'] = self.locked()
        result['displayed'] = self.displayed()
        result['default'] = self.default()
        result['preset'] = self.preset()
        return result
