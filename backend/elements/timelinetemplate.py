from noapiframe import ElementBase, docDB


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

    def save_post(self):
        from helpers.wss import transmit_timelinetemplate_update
        transmit_timelinetemplate_update(self)

    def delete_post(self):
        from elements import Timeline
        from helpers.wss import transmit_timelinetemplate_delete
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'template_id': self['_id']})]:
            t['template_id'] = None
            t.save()
        transmit_timelinetemplate_delete(self)

    def update_timelines(self):
        from elements import Timeline
        result = list()
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'template_id': self['_id']})]:
            if not t.locked():
                t['screen_ids'] = list()
                for s in self['screen_ids']:
                    t['screen_ids'].append(s)
                t.save()
                result.append(t['_id'])
        return result
