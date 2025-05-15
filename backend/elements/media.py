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
