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

    def validate(self):
        errors = dict()
        if self['timeline_id'] is not None and self.timeline().preset():
            errors['_id'] = {'code': 80, 'desc': "Timeline is part of a Preset and therefore can't be displayed"}
        return errors

    def delete_pre(self):
        self['timeline_id'] = None
        self.save()

    def delete_post(self):
        from elements import Timeline
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'kiosk_id': self['_id']})]:
            t.delete()
