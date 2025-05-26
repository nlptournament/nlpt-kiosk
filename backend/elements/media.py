from noapi import ElementBase


class Media(ElementBase):
    """
Do some description
    """
    _attrdef = dict(
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        src_type=ElementBase.addAttr(type=int, default=0, notnone=True),
        src=ElementBase.addAttr(type=str, default='', notnone=True),
        type=ElementBase.addAttr(type=int, default=0, notnone=True),
        user_id=ElementBase.addAttr(type=str, default=None, fk='User'),
        common=ElementBase.addAttr(type=bool, default=True, notnone=True)
    )

    def validate(self):
        errors = dict()
        if self['src_type'] not in range(2):
            errors['src_type'] = {'code': 5, 'desc': 'needs to be one of: [0, 1]'}
        if self['type'] not in range(3):
            errors['type'] = {'code': 5, 'desc': 'needs to be one of: [0, 1, 2]'}
        return errors

    def save_post(self):
        from helpers.wss import transmit_media_update
        transmit_media_update(self)

    def delete_post(self):
        from helpers.wss import transmit_media_delete
        if self['src_type'] == 1:
            from helpers.s3 import media_delete, media_exists
            if media_exists(self['_id']):
                media_delete(self['_id'])
        transmit_media_delete(self)
