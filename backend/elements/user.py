from noapi import docDB
from noapi.elements import UserBase


class User(UserBase):
    def delete_pre(self):
        from elements import Screen
        for s in [Screen(s) for s in docDB.search_many('Screen', {'user_id': self['_id']})]:
            if s.locked():
                return {'error': {'code': 1, 'desc': 'at least one locked Screen is using this User'}}

    def delete_post(self):
        from elements import Session, TimelineTemplate, Screen
        for s in [Session(s) for s in docDB.search_many('Session', {Session.__userid_field: self['_id']})]:
            s.delete()
        for tt in [TimelineTemplate(tt) for tt in docDB.search_many('TimelineTemplate', {'user_id': self['_id']})]:
            tt.delete()
        for s in [Screen(s) for s in docDB.search_many('Screen', {'user_id': self['_id']})]:
            s.delete()
