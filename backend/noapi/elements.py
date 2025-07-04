import cherrypy
from datetime import datetime
from .docdb import docDB
from .client import get_client_ip


class ElementBase(object):
    _attrdef = dict()

    def __init__(self, attr=None):
        self._cache = dict()
        self._attr = dict()
        if '_id' not in self.__class__._attrdef.keys():
            self.__class__._attrdef = {**{'_id': self.__class__.addAttr(type=str, default=None, unique=True)}, **self.__class__._attrdef}  # add _id on front
        self.__init_attr()
        if attr is not None:
            for k, v in attr.items():
                self[k] = v

    def __init_attr(self):
        def make_func(element, attr):
            def _func(self, set_to=None):
                if set_to is not None:
                    self[attr] = set_to['_id']
                else:
                    if 'fk' not in self._cache:
                        self._cache['fk'] = dict()
                    if attr not in self._cache['fk']:
                        self._cache['fk'][attr] = None
                    if self._cache['fk'][attr] is None:
                        mod = __import__('elements', fromlist=[element])
                        cls = getattr(mod, element)
                        self._cache['fk'][attr] = cls.get(self[attr])
                    return self._cache['fk'][attr]
            return _func

        for name, attrdef in self.__class__._attrdef.items():
            self._attr[name] = attrdef['default']
            if attrdef['fk'] is not None and attrdef['type'] is str:
                func = make_func(attrdef['fk'], name)
                setattr(self.__class__, name.rstrip('_id'), func)

    def __getitem__(self, key):
        return self._attr.get(key, None)

    def __setitem__(self, key, value):
        if key in self._attr:
            self._attr[key] = value
            if self._attrdef[key]['fk'] is not None and 'fk' in self._cache and key in self._cache['fk']:
                self._cache['fk'][key] = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self['_id'] is None or other['_id'] is None:
                return False
            elif self['_id'] == other['_id']:
                return True
        return False

    def __str__(self):
        return str(self._attr)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self['_id']}>"

    def addAttr(type=str, default=None, unique=False, notnone=False, fk=None):
        return {'type': type, 'default': default, 'unique': unique, 'notnone': notnone, 'fk': fk}

    @classmethod
    def exists(cls, id):
        return docDB.exists(cls.__name__, id)

    @classmethod
    def get(cls, id):
        result = cls()
        fromdb = docDB.get(cls.__name__, id)
        if fromdb is not None:
            for k, v in fromdb.items():
                result._attr[k] = v
        return result

    @classmethod
    def all(cls):
        result = list()
        for element in docDB.search_many(cls.__name__, {}):
            result.append(cls(element))
        return result

    @classmethod
    def count(cls, filter={}):
        return docDB.count(cls.__name__, filter)

    def validate_base(self):
        errors = dict()
        for attr, opt in self.__class__._attrdef.items():
            if attr == '_id':
                continue
            if opt['notnone']:
                if self[attr] is None:
                    errors[attr] = {'code': 1, 'desc': 'marked as not to be None'}
                    continue
            if opt['unique'] and not (self[attr] is None and not opt['notnone']):
                found = docDB.search_one(self.__class__.__name__, {attr: self[attr]})
                if found is not None and not found['_id'] == self['_id']:
                    errors[attr] = {'code': 2, 'desc': f'marked as unique, but element with value "{self[attr]}" allready present'}
                    continue
            if not isinstance(self[attr], opt['type']) and self[attr] is not None:
                errors[attr] = {'code': 3, 'desc': f"needs to be of type {opt['type']}{' or None' if not opt['notnone'] else ''}"}
            if opt['fk'] is not None and self[attr] is not None:
                if opt['type'] is str:
                    if not docDB.exists(opt['fk'], self[attr]):
                        errors[attr] = {'code': 4, 'desc': f"there is no {opt['fk']} with id '{self[attr]}'"}
                elif opt['type'] is list:
                    for element_id in self[attr]:
                        if not docDB.exists(opt['fk'], element_id):
                            errors[attr] = {'code': 4, 'desc': f"there is no {opt['fk']} with id '{element_id}'"}
                            break
        if len(errors) == 0:
            errors = self.validate()
        return errors

    def validate(self):
        return dict()

    def save(self, only_on_changes=False):
        errors = self.validate_base()
        if not len(errors) == 0:
            return {'errors': errors}

        if only_on_changes:
            fromdb = docDB.get(self.__class__.__name__, self['_id'])
            if fromdb is not None:
                for k, v in self._attr.items():
                    if k not in fromdb:
                        break
                    if not v == fromdb[k]:
                        break
                else:
                    return {'no change': self['_id']}

        self.save_pre()
        if self['_id'] is None:
            docDB.create(self.__class__.__name__, self._attr)
            result = 'created'
        else:
            docDB.replace(self.__class__.__name__, self._attr)
            result = 'updated'
        self.save_post()

        return {result: self['_id']}

    def save_pre(self):
        pass

    def save_post(self):
        pass

    def delete(self):
        saved_id = self['_id']
        if self['_id'] is not None and docDB.exists(self.__class__.__name__, self['_id']):
            pre_delete_result = self.delete_pre()
            if pre_delete_result is not None and 'error' in pre_delete_result:
                return pre_delete_result
            docDB.delete(self.__class__.__name__, self['_id'])
            self.delete_post()
        self.__init_attr()
        return {'deleted': saved_id}

    def delete_pre(self):
        pass

    def delete_post(self):
        pass

    def reload(self):
        fromdb = docDB.get(self.__class__.__name__, self['_id'])
        if fromdb is not None:
            self._attr = fromdb

    def drop_cache(self):
        self._cache = dict()

    def json(self):
        result = {**{'id': self['_id']}, **self._attr}
        result.pop('_id', None)
        return result


class SettingBase(ElementBase):
    _attrdef = dict(
        type=ElementBase.addAttr(default='str', notnone=True),
        value=ElementBase.addAttr(type=object, default=None),
        order=ElementBase.addAttr(type=int, default=0, notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True)
    )

    _valid_types = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool
    }

    """
    dict of default values (and their type and description) for system-settings
    key is the "name" of value, value is a dict itself containing the following keys:
      type: as sting, one key of the dict _valid_types (see above)
      value: the default value (might be None)
      order: integer defining the sort-order (of all Settings) in frontend
      desc: string describing the purpose of the setting
    example:
      'server_port': {'type': 'int', 'value': 8000, 'desc': 'Port the backend should be listening on'}
    """
    _defaults = dict()

    @classmethod
    def all(cls):
        result = list()
        keys = list()
        for element in docDB.search_many(cls.__name__, {}):
            result.append(cls(element))
            keys.append(element['_id'])
        for k in cls._defaults.keys():
            if k not in keys:
                result.append(cls.get(k))
        return result

    @classmethod
    def get(cls, key):
        result = cls()
        result._attr['_id'] = key
        fromdb = docDB.get(cls.__name__, key)
        if fromdb is not None:
            result._attr = fromdb
        elif key in cls._defaults:
            result._attr = cls._defaults[key]
            result._attr['_id'] = key
        return result

    @classmethod
    def value(cls, key):
        c = cls.get(key)
        if c is None:
            return None
        else:
            return c['value']

    @classmethod
    def set(cls, key, value):
        c = cls.get(key)
        if c is None:
            attr = dict()
            if key in cls._defaults:
                attr = cls._defaults[key]
            c = cls(attr)
        c['_id'] = key
        c['value'] = value
        return c.save()

    def validate(self):
        errors = dict()
        if self['type'] not in self._valid_types.keys():
            errors['type'] = {'code': 5, 'desc': f'needs to be one of: {list(self._valid_types.keys())}'}
        elif not isinstance(self['value'], self._valid_types[self['type']]) and self['value'] is not None:
            errors['value'] = {'code': 3, 'desc': f"needs to be of type {self._valid_types[self['type']]} or None"}
        return errors

    def save_pre(self):
        if self['_id'] in self._defaults:
            self['desc'] = self._defaults[self['_id']]['desc']


class UserBase(ElementBase):
    _attrdef = dict(
        admin=ElementBase.addAttr(type=bool, default=False, notnone=True),
        login=ElementBase.addAttr(type=str, unique=True, default=None),
        pw=ElementBase.addAttr(type=str, default=None)
    )

    @classmethod
    def get_by_login(cls, login):
        result = cls()
        fromdb = docDB.search_one(cls.__name__, {'login': login})
        if fromdb is not None:
            result._attr = fromdb
            return result
        return None


class SessionBase(ElementBase):
    cookie_name = 'noAPI'  # Set this in your deriveing class to a desired name, used for storing the session-cookie, in browsers
    _user_cls = UserBase  # Set this to a child-class of UserBase in your deriveing class

    _attrdef = dict(
        till=ElementBase.addAttr(type=int, notnone=True),
        ip=ElementBase.addAttr(type=str, default=None, notnone=True),
        complete=ElementBase.addAttr(type=bool, default=False),
        user_id=ElementBase.addAttr(type=str, notnone=True)
    )

    def validate(self, request_addr=None):
        errors = dict()
        if not docDB.exists(self._user_cls.__name__, self['user_id']):
            errors['user_id'] = {'code': 4, 'desc': f"there is no {self._user_cls.__name__} with id '{self['user_id']}'"}
        if self['till'] <= int(datetime.now().timestamp()):
            errors['till'] = {'code': 10, 'desc': 'needs to be in the future'}
        if request_addr is not None:
            if not self['if'] == request_addr:
                errors['ip'] = {'code': 11, 'desc': 'does not match with the IP of request'}
        elif cherrypy.request:
            if not self['ip'] == get_client_ip():
                errors['ip'] = {'code': 11, 'desc': 'does not match with the IP of request'}
        if len(errors) > 0:
            self.delete()
        return errors

    def delete_others(self):
        for sd in docDB.search_many(self.__class__.__name__, {'user_id': self['user_id'], '_id': {'$ne': self['_id']}}):
            s = self.__class__(sd)
            s.delete()

    def admin(self):
        u = docDB.get(self._user_cls.__name__, self['user_id'])
        if u is not None:
            return u.get('admin', False)
        return False
