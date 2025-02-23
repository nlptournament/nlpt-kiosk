from noapi import ElementBase


class ScreenTemplate(ElementBase):
    _attrdef = dict(
        key=ElementBase.addAttr(type=str, default='', notnone=True),
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        endless=ElementBase.addAttr(type=bool, default=True, notnone=True),
        duration=ElementBase.addAttr(type=int, default=None),
        variables_def=ElementBase.addAttr(type=dict, default=dict(), notnone=True)
    )
