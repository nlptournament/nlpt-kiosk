from noapiframe import docDB
from noapiframe.elements import UserBase


class User(UserBase):
    """
Representation of a User, that is able to login and administrate Kiosks

streamer : bool
    Users with this attribute set to True are redirected to streamer-screen after login (but are also able to access the regular admin-screen)
hidden_elements : list[str]
    list of element id's to hide in frontend for this User
    """

    UserBase._attrdef['streamer'] = UserBase.addAttr(type=bool, default=False, notnone=True)
    UserBase._attrdef['hidden_elements'] = UserBase.addAttr(type=list, default=[], notnone=True)

    def save_post(self):
        from helpers.wss import transmit_user_update
        transmit_user_update(self)

    def delete_pre(self):
        from elements import Screen
        for s in [Screen(s) for s in docDB.search_many('Screen', {'user_id': self['_id']})]:
            if s.locked():
                return {'error': {'code': 1, 'desc': 'at least one locked Screen is using this User'}}

    def delete_post(self):
        from elements import Session, TimelineTemplate, Screen, Kiosk, Preset, Media
        from helpers.wss import transmit_user_delete
        for s in [Session(s) for s in docDB.search_many('Session', {'user_id': self['_id']})]:
            s.delete()
        for p in [Preset(p) for p in docDB.search_many('Preset', {'user_id': self['_id']})]:
            p.delete()
        for t in [TimelineTemplate(t) for t in docDB.search_many('TimelineTemplate', {'user_id': self['_id']})]:
            t.delete()
        for s in [Screen(s) for s in docDB.search_many('Screen', {'user_id': self['_id']})]:
            s.delete()
        for k in [Kiosk(k) for k in docDB.search_many('Kiosk', {'added_by_id': self['_id']})]:
            k['added_by_id'] = None
            k.save()
        for m in [Media(m) for m in docDB.search_many('Media', {'user_id': self['_id']})]:
            m['user_id'] = None
            m.save()
        transmit_user_delete(self)
