from noapi import ElementBase, docDB


class Kiosk(ElementBase):
    """
Kiosk is the representation of a displaying device

name : str
    unique identifier for the frontend-instance (displaying device)
desc : str
    some useful description
added_by_id : str | None
    the User who added or accepted Kiosk in the system. defines the owner.
    if it is None the Kiosk is not yet accepted by an admin.
common : bool (default: False)
    if True Kiosk is available to all Users, if False only available to owner and admins.
timeline_id : str | None
    Timeline, that is currently displayed on Kiosk. if it is None the related displaying device is showing nothing.
    """
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, notnone=True, unique=True),
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        added_by_id=ElementBase.addAttr(type=str, default=None, fk='User'),
        common=ElementBase.addAttr(type=bool, default=False, notnone=True),
        timeline_id=ElementBase.addAttr(type=str, default=None, fk='Timeline')
    )

    @classmethod
    def id_by_name(cls, name):
        fromdb = docDB.search_one(cls.__name__, {'name': name})
        if fromdb is not None:
            return fromdb['_id']
        else:
            k = cls()
            k['name'] = name
            return k.save()['created']

    def validate(self):
        errors = dict()
        if self['timeline_id'] is not None and self.timeline().preset():
            errors['_id'] = {'code': 80, 'desc': "Timeline is part of a Preset and therefore can't be displayed"}
        return errors

    def save_pre(self):
        if self['_id'] is not None:
            from_db = docDB.get(self.__class__.__name__, self['_id'])
            if from_db is not None:
                self._cache['old_timeline_id'] = from_db.get('timeline_id', None)

    def save_post(self):
        from helpers.wss import transmit_kiosk_update, transmit_timeline_update, transmit_screen_update
        from elements import Timeline, Screen
        transmit_kiosk_update(self)
        t = Timeline.get(self['timeline_id'])
        for s in [Screen.get(s) for s in t['screen_ids']]:
            transmit_screen_update(s)
        transmit_timeline_update(t)
        if 'old_timeline_id' in self._cache and self._cache['old_timeline_id'] is not None and not self._cache['old_timeline_id'] == self['timeline_id']:
            t = Timeline.get(self._cache['old_timeline_id'])
            t.save()

    def delete_pre(self):
        self['timeline_id'] = None
        self.save()

    def delete_post(self):
        from elements import Timeline
        from helpers.wss import transmit_kiosk_delete
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'kiosk_id': self['_id']})]:
            t.delete()
        transmit_kiosk_delete(self)
