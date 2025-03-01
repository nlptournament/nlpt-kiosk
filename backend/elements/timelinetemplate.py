from noapi import ElementBase


class TimelineTemplate(ElementBase):
    """
Defines a template for Timelines. TimelineTemplates are used as an easy way to populate (and update) multiple Kiosks with a Timeline

desc : str
    some helpful description
user_id : str
    creator/owner of the TimelineTemplate
screen_ids : list
    list of Screens used by this TimelineTemplate, this also sets the order of apperance on the Kiosk

update_timelines()
    writes screen_ids to linked (unlocked) Timelines
    """
    _attrdef = dict(
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        user_id=ElementBase.addAttr(type=str, notnone=True, fk='User'),
        screen_ids=ElementBase.addAttr(type=list, default=list(), notnone=True, fk='Screen')
    )

    def update_timelines(self):
        raise NotImplementedError
