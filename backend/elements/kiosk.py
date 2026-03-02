from noapiframe import ElementBase, docDB


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
    Timeline, that is currently displayed on Kiosk. If it is None the related displaying device is showing nothing.
default_timeline_id : str | None
    Timeline, that is defined as the default for this Kiosk, which can be applied with a quick-access.

apply_default() : bool
    Sets the default_timeline_id as timeline_id with resetting the current_pos of Timeline
    returns False if default_timeline_id is None, otherwise True
apply_timelinetemplate(template_id) : bool
    Accepts a TimelineTemplate id, creates a Timeline of of this, and applys it as the active Timeline for the Kiosk
    """
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, notnone=True, unique=True),
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        added_by_id=ElementBase.addAttr(type=str, default=None, fk='User'),
        common=ElementBase.addAttr(type=bool, default=True, notnone=True),
        timeline_id=ElementBase.addAttr(type=str, default=None, fk='Timeline'),
        default_timeline_id=ElementBase.addAttr(type=str, default=None, fk='Timeline')
    )

    @classmethod
    def id_by_name(cls, name, allow_create=False):
        fromdb = docDB.search_one(cls.__name__, {'name': name})
        if fromdb is not None:
            return fromdb['_id']
        elif allow_create:
            k = cls()
            k['name'] = name
            return k.save()['created']
        else:
            return None

    def validate(self):
        errors = dict()
        if self['timeline_id'] is not None and self.timeline().preset():
            errors['_id'] = {'code': 80, 'desc': "Timeline is part of a Preset and therefore can't be displayed"}
        return errors

    def save_pre(self):
        from elements import Timeline
        if self['_id'] is not None:
            from_db = docDB.get(self.__class__.__name__, self['_id'])
            if from_db is not None:
                self._cache['old_timeline_id'] = from_db.get('timeline_id', None)
                self._cache['old_default_timeline_id'] = from_db.get('default_timeline_id', None)
        if self['default_timeline_id'] is not None:
            t = Timeline.get(self['default_timeline_id'])
            if t['single_shot']:
                t['single_shot'] = False
                t.save()

    def save_post(self):
        from helpers.wss import transmit_kiosk_update, transmit_timeline_update, transmit_screen_update
        from elements import Timeline, Screen
        transmit_kiosk_update(self)
        if self['timeline_id'] is not None:
            t = Timeline.get(self['timeline_id'])
            for s in [Screen.get(s) for s in t['screen_ids']]:
                transmit_screen_update(s)
            transmit_timeline_update(t)
        if self['default_timeline_id'] is not None:
            t = Timeline.get(self['default_timeline_id'])
            for s in [Screen.get(s) for s in t['screen_ids']]:
                transmit_screen_update(s)
            transmit_timeline_update(t)
        if 'old_timeline_id' in self._cache and self._cache['old_timeline_id'] is not None and not self._cache['old_timeline_id'] == self['timeline_id']:
            t = Timeline.get(self._cache['old_timeline_id'])
            if t['single_shot']:
                t.delete()
            else:
                t.save()  # To reset current_pos on Timeline
        if (
            'old_default_timeline_id' in self._cache
            and self._cache['old_default_timeline_id'] is not None
            and not self._cache['old_default_timeline_id'] == self['default_timeline_id']
        ):
            t = Timeline.get(self._cache['old_default_timeline_id'])
            transmit_timeline_update(t)

    def delete_pre(self):
        self['timeline_id'] = None
        self.save()

    def delete_post(self):
        from elements import Timeline
        from helpers.wss import transmit_kiosk_delete
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'kiosk_id': self['_id']})]:
            t.delete()
        transmit_kiosk_delete(self)

    def apply_default(self):
        if self['default_timeline_id'] is None:
            return False
        else:
            from elements import Timeline
            self['timeline_id'] = None
            self.save()
            t = Timeline.get(self['default_timeline_id'])
            t.save()
            self['timeline_id'] = self['default_timeline_id']
            self.save()
            return True

    def apply_timelinetemplate(self, template_id):
        from elements import TimelineTemplate, Timeline
        if self['_id'] is None:
            return False
        if self['default_timeline_id'] is None:
            return False
        tt = TimelineTemplate.get(template_id)
        if tt['_id'] is None:
            return False
        tl = Timeline({'template_id': template_id, 'kiosk_id': self['_id'], 'screen_ids': tt['screen_ids'], 'single_shot': True})
        tl.save()
        self['timeline_id'] = tl['_id']
        self.save()
        return False
