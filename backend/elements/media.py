from noapi import ElementBase


class Media(ElementBase):
    """
Media objects are a container for providing images, animations oder videos so Screens, that can handle them

desc : str
    some useful description
src_type : int (default: 0)
    defines where the media-file is stored, needs to be one of:
        0: generic web URL
        1: internal S3 storage
src : str
    in case of src_type == 0 this field stores the web-URL of media-file
    in case of src_type == 1 this field contains some meta-information about media-file (should not be modified by User)
type : int (default: 0)
    defines the class of Media, needs to be one of:
        0: static image
        1: animated image
        2: video
user_id : str | None
    creator/owner of Media, gets None if the corresponding User is deleted
common : bool (default: True)
    if True Media is available to all Users, if False only available to owner and admins
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
