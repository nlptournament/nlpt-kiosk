import cherrypy
import cherrypy_cors
import hashlib
from datetime import datetime
from .client import get_client_ip


@cherrypy.popargs('element_id')
class ElementEndpointBase(object):
    _element = None  # Set this to the element-class you like to serve vir API
    _session_cls = None  # Set this to a child-class of SessionBase in your deriveing class
    _restrict_read = True  # if set to True only admin Users are allowed to use reading methods
    _restrict_write = True  # if set to True only admin Users are allowed to use writing methods
    _ro_attr = list()  # List of attribute-names, that are allways read-only

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, element_id=None):
        if cherrypy.request.method == 'OPTIONS':
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST, DELETE'
                cherrypy_cors.preflight(allowed_methods=['GET', 'POST', 'DELETE'])
                return
            else:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy_cors.preflight(allowed_methods=['GET', 'PATCH', 'DELETE'])
                return

        cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
        if cookie:
            session = self._session_cls.get(cookie.value)
        else:
            session = self._session_cls.get(None)
        if len(session.validate_base()) > 0:
            cherrypy.response.status = 401
            return {'error': 'not authorized'}

        if cherrypy.request.method == 'GET':
            if self._restrict_read and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is not None:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                return el.json()
            else:
                result = list()
                for el in self._element.all():
                    result.append(el.json())
                return result
        elif cherrypy.request.method == 'POST':
            if self._restrict_write and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is None:
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                elif len(attr) == 0:
                    cherrypy.response.status = 400
                    return {'error': 'data is needed to be submitted'}
                attr.pop('_id', None)
                for ro in self._ro_attr:
                    attr.pop(ro, None)
                el = self._element(attr)
                result = el.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy.response.status = 405
                return {'error': 'POST not allowed on existing objects'}
        elif cherrypy.request.method == 'PATCH':
            if self._restrict_write and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy.response.status = 405
                return {'error': 'PATCH not allowed on indexes'}
            else:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                attr.pop('_id', None)
                for k, v in attr.items():
                    if k not in self._ro_attr:
                        el[k] = v
                result = el.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result
        elif cherrypy.request.method == 'DELETE':
            if self._restrict_write and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is None:
                deleted_ids = list()
                for el in self._element.all():
                    r = el.delete()
                    if 'delete' in r:
                        deleted_ids.append(r['delete'])
                return {'deleted': deleted_ids}
            else:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                result = el.delete()
                if 'deleted' not in result:
                    cherrypy.response.status = 400
                return result
        else:
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST, DELETE'
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}


@cherrypy.popargs('element_id')
class SettingEndpointBase(object):
    _setting_cls = None  # Set this to a child-class of SettingBase in your deriveing class
    _session_cls = None  # Set this to a child-class of SessionBase in your deriveing class
    _restrict_read = False  # if set to True only admin Users are allowed to use reading methods (in this case, leave as is)
    _restrict_write = True  # if set to True only admin Users are allowed to use writing methods (in this case, leave as is)
    _ro_attr = list()  # List of attribute-names, that are allways read-only (in this case, leave as is)
    user_readable = list()  # List of Settings that are publicly readable
    admin_writeable = list()  # List of Settings, that are only exposed to and writeable by admins

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, element_id=None):
        if cherrypy.request.method == 'OPTIONS':
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
                cherrypy_cors.preflight(allowed_methods=['GET'])
                return
            else:
                el = self._setting_cls.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH'
                cherrypy_cors.preflight(allowed_methods=['GET', 'PATCH'])
                return

        cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
        if cookie:
            session = self._session_cls.get(cookie.value)
        else:
            session = self._session_cls.get(None)
        admin = len(session.validate_base()) == 0 and session.admin()

        if cherrypy.request.method == 'GET':
            if self._restrict_read and not admin:
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is not None:
                el = self._setting_cls.get(element_id)
                if el['_id'] is not None and (admin or el['_id'] in self.user_readable):
                    result = el.json()
                    result['ro'] = True if not admin or element_id not in self.admin_writeable else False
                    return result
                else:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
            else:
                result = list()
                for el in self._setting_cls.all():
                    if admin or el['_id'] in self.user_readable:
                        r = el.json()
                        r['ro'] = True if not admin or el['_id'] not in self.admin_writeable else False
                        result.append(r)
                return result
        elif cherrypy.request.method == 'PATCH':
            if self._restrict_write and not admin:
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
                cherrypy.response.status = 405
                return {'error': 'PATCH not allowed on indexes'}
            else:
                el = self._setting_cls.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                if element_id not in self.admin_writeable:
                    cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
                    cherrypy.response.status = 405
                    return {'error': f'{element_id} is read-only'}
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                attr.pop('_id', None)
                for k, v in attr.items():
                    if k not in self._ro_attr:
                        el[k] = v
                result = el.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result
        else:
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}


class LoginEndpointBase(object):
    _session_cls = None  # Set this to a child-class of SessionBase in your deriveing class

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, user=None):
        cookie_name = self._session_cls.cookie_name
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST, PUT'
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST', 'PUT'])
            return
        elif cherrypy.request.method == 'GET':
            if user is not None:
                p = self._session_cls._user_cls.get_by_login(user)
                if p is not None:
                    s = self._session_cls({self._session_cls.__userid_field: p['_id'], 'complete': False, 'ip': get_client_ip()})
                    s['till'] = int(datetime.now().timestamp() + 300)
                    cookie = cherrypy.response.cookie
                    cookie[cookie_name] = s.save().get('created')
                    cookie[cookie_name]['path'] = '/'
                    cookie[cookie_name]['max-age'] = 300
                    cookie[cookie_name]['version'] = 1
                    cherrypy.response.status = 201
                    return {'session_id': s['_id'], 'till': s['till'], 'complete': s['complete']}
                else:
                    cherrypy.response.status = 400
                    return {'error': 'invalid user'}
            else:
                c = cherrypy.request.cookie.get(cookie_name)
                if c:
                    s = self._session_cls.get(c.value)
                else:
                    s = self._session_cls.get(None)
                if len(s.validate_base()) == 0:
                    cherrypy.response.status = 201
                    return {'session_id': s['_id'], 'till': s['till'], 'complete': s['complete']}
                else:
                    cherrypy.response.status = 400
                    return {'error': 'invalid session'}
        elif cherrypy.request.method == 'POST':
            attr = cherrypy.request.json
            if not isinstance(attr, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}
            elif len(attr) == 0:
                cherrypy.response.status = 400
                return {'error': 'data is needed to be submitted'}
            elif 'pw' not in attr:
                cherrypy.response.status = 400
                return {'error': 'pw is missing in data'}
            c = cherrypy.request.cookie.get(cookie_name)
            if c:
                s = self._session_cls.get(c.value)
            else:
                s = self._session_cls.get(None)
            if not len(s.validate_base()) == 0:
                cherrypy.response.status = 400
                return {'error': 'invalid session'}
            else:
                p = self._session_cls._user_cls.get(s[self._session_cls.__userid_field])
                m = hashlib.md5()
                m.update(s['_id'].encode('utf-8'))
                m.update(p['pw'].encode('utf-8'))
                if not m.hexdigest().lower() == attr['pw'].lower():
                    s.delete()
                    cherrypy.response.status = 400
                    return {'error': 'invalid password'}
                else:
                    s['complete'] = True
                    s['till'] = int(datetime.now().timestamp() + 60 * 60 * 24)
                    s.save()
                    s.delete_others()
                    cookie = cherrypy.response.cookie
                    cookie[cookie_name] = s['_id']
                    cookie[cookie_name]['path'] = '/'
                    cookie[cookie_name]['max-age'] = 60 * 60 * 24
                    cookie[cookie_name]['version'] = 1
                    cherrypy.response.status = 201
                    return {'session_id': s['_id'], 'till': s['till'], 'complete': s['complete']}
        elif cherrypy.request.method == 'PUT':
            c = cherrypy.request.cookie.get(cookie_name)
            if c:
                s = self._session_cls.get(c.value)
                s.delete()
            cherrypy.response.status = 201
            return {'logout': 'done'}
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
