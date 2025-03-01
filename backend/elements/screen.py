from noapi import ElementBase, docDB


class Screen(ElementBase):
    """
Screens are the element placed on Timelines and define what is displayed on a kiosk and how

desc : str
    some helpful description
template_id : str
    the parent template a Screen inherits from
user_id : str
    creator/owner of a Screen
duration : int | None
    how long the Screen is displayed on Timeline (in seconds). needs to be bigger than 0 or None.
    can only be changed if template is endless, otherwise copied from template
repeat : int (default: 0)
    number of times to repeat Screen. 0 means show once then go on. needs to be 0 or bigger.
    only possible to change if template is not endless, otherwise set to 0
loop : bool (default: False)
    like repeat but infinite. only possible to change if template is not endless, otherwise set to False
variables : dict
    variables content passed to the frontend. only variables defined in Template are allowed (saved).
    key is the variable name and value the value to pass over. type of variable needs to match the one define in Template.
    if variables (with default value in Template) are missing on saving, the are pulled over from Template.

locked() : bool
    if True, it's not allowed to change Screen, as it is used bei locked Timelines.
    gets True if Screen is part of at least one locked Timeline
key() : str
    shortcut to ScreenTemplate's key
    """
    _attrdef = dict(
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        template_id=ElementBase.addAttr(type=str, notnone=True, fk='ScreenTemplate'),
        user_id=ElementBase.addAttr(type=str, notnone=True, fk='User'),
        duration=ElementBase.addAttr(type=int, default=None),
        repeat=ElementBase.addAttr(type=int, default=0, notnone=True),
        loop=ElementBase.addAttr(type=bool, default=False, notnone=True),
        variables=ElementBase.addAttr(type=dict, default=dict(), notnone=True)
    )

    def validate(self):
        errors = dict()
        if self['_id'] is not None and self.locked():
            errors['_id'] = {'code': 50, 'desc': "Screen can't be changed, as it is used in a locked Timeline"}
        if self['duration'] is not None and self['duration'] < 1:
            errors['duration'] = {'code': 7, 'desc': 'needs to be bigger than 0 or Null'}
        if self['repeat'] < 0:
            errors['repeat'] = {'code': 7, 'desc': 'needs to be 0 or bigger'}
        # variables validation
        missing_variables = list()
        for k, v in self.template()['variables_dev'].items():
            if k not in self['variables']:
                if 'default' in v:
                    self['variables'][k] = v['default']
                else:
                    missing_variables.append(k)
            if not isinstance(self['variables'][k], self.template()._valid_types[v['type']]):
                errors['variables'] = {'code': 3, 'desc': f"'{k}' needs to be of type {v['type']}"}
        if len(missing_variables) > 0:
            errors['variables'] = {'code': 51, 'desc': f'missing the variables: {missing_variables}'}
        return errors

    def save_pre(self):
        if self.template()['endless']:
            self['repeat'] = 0
            self['loop'] = False
        else:
            self['duration'] = self.template()['duration']
        for k, v in self.template()['variables_def'].items():
            if 'ro' in v and v['ro']:
                self['variables'][k] = v['default']
        if not len(self['variables']) == len(self.template()['variables_def']):
            variables_to_remove = list()
            for k in self['variables'].keys():
                if k not in self.template()['variables_def']:
                    variables_to_remove.append(k)
            for k in variables_to_remove:
                self['variables'].pop(k, None)

    def delete_pre(self):
        if self.locked():
            return {'error': {'code': 2, 'desc': "can't be deleted as it is locked"}}

    def delete_post(self):
        from elements import TimelineTemplate, Timeline
        for t in [TimelineTemplate(t) for t in docDB.search_many('TimelineTemplate', {'screen_ids': self['_id']})]:
            t['screen_ids'].remove(self['_id'])
            t.save()
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'screen_ids': self['_id']})]:
            t['screen_ids'].remove(self['_id'])
            t.save()

    def locked(self):
        from elements import Timeline
        for t in [Timeline(t) for t in docDB.search_many('Timeline', {'screen_ids': self['_id']})]:
            if t.locked():
                return True
        return False

    def key(self):
        return self.template()['key']
