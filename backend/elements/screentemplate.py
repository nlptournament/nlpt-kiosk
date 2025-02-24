from noapi import ElementBase


class ScreenTemplate(ElementBase):
    _attrdef = dict(
        key=ElementBase.addAttr(type=str, default='', notnone=True),
        desc=ElementBase.addAttr(type=str, default='', notnone=True),
        endless=ElementBase.addAttr(type=bool, default=True, notnone=True),
        duration=ElementBase.addAttr(type=int, default=None),
        variables_def=ElementBase.addAttr(type=dict, default=dict(), notnone=True)
    )

    _valid_types = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool
    }

    def validate(self):
        errors = dict()
        if self['key'] == '':
            errors['key'] = {'code': 6, 'desc': 'not allowed to be empty'}
        if self['duration'] is not None and self['duration'] < 1:
            errors['duration'] = {'code': 7, 'desc': 'needs to be bigger than 0 or Null'}
        for k, v in self['variables_def'].items():
            if 'type' not in v:
                errors['variables_def'] = {'code': 40, 'desc': f"missing the parameter 'type' in definition of '{k}'"}
            elif not isinstance(v['type'], str):
                errors['variables_def'] = {'code': 3, 'desc': f"parameter 'type' in definition of '{k}' needs to be of type str"}
            elif v['type'] not in self._valid_types.keys():
                errors['variables_def'] = {'code': 5, 'desc': f"parameter 'type' in definition of '{k}' needs to be one of: {self._valid_types.keys()}"}
            elif 'default' in v and not isinstance(v['default'], self._valid_types[v['type']]):
                errors['variables_def'] = {'code': 41, 'desc': f"default value in definition of '{k}' is not of type '{v['type']}'"}
        return errors
