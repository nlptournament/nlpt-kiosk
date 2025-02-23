from noapi import docDB
from noapi.elements import UserBase


class User(UserBase):
    def delete_post(self):
        from elements import Session
        for s in [Session(s) for s in docDB.search_many('Session', {Session.__userid_field: self['_id']})]:
            s.delete()
