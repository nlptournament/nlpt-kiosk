import cherrypy
import cherrypy_cors
import hashlib
from datetime import datetime
from .client import get_client_ip


@cherrypy.popargs('element_id')
class ElementEndpointBase(object):
    """
Defines an generic Endpoint for handling Elements via API, that most of your Endpoints should derive from.

_element : cls
    Set this to the Element-class you like to serve via API
_session_cls : cls
    Set this to a child-class of SessionBase in your deriveing class
_owner_attr : str | None
    Set this to an attr-name which determines the the owner of an Element, an owner does have the same privileges as an admin.
    This attr needs to be a fk of UserBase deriveing class. If it is None this Element does not have an owner in it's design.
_other_attr : str | None
    Set this to an attr-name which determines if the Element is available to other Users than owner and admin.
    The attr needs to return True if the Element is available to others, otherwise they are handeled like all (unauthorized) Users.
    If this variable is None the other rules (see below) are applied for all other Users.
_other_readable : list | None
    list of attr-names which are readable for other Users. If None, Endpoint is not available for other Users reads.
_other_createable : list | None
    list of attr-names which are writeable for other Users, when creating an Element.
    If None, Endpoint is not available for other Users to create an Element.
_other_updateable : list | None
    list of attr-names which are writeable for other Users, when updating an Element.
    If None, Endpoint is not available for other Users to update an Element.
_other_delete : bool
    if set to True other Users are allowed to delete Elements on Endpoint (by default only admins and owners are allowed to delete)
_all_readable : list | None
    list of attr-names which are readable for all (unauthorized) Users. If None, Endpoint is not available for unauthorized reads.
_all_createable : list | None
    list of attr-names which are writeable for all (unauthorized) Users, when creating an Element.
    If None, Endpoint is not available for unauthorized Element creations.
_all_updateable : list | None
    list of attr-names which are writeable for all (unauthorized) Users, when updating an Element.
    If None, Endpoint is not available for unauthorized Element updates.
_all_delete : bool
    if set to True all (unauthorized) Users are allowed to delete Elements on Endpoint (by default only admins and owners are allowed to delete)
_not_readable : list
    List of attr-names, that are deleted from GET responses (e.g. useful for passwords that shouldn't be exposed)
_not_updateable : list
    List of attr-names, that are deleted from PATCH requests but passed trough on POST requests
_ro_attr : list
    List of attr-names, that are always read-only (deleted from POST and PATCH requests)
    """
    _element = None
    _session_cls = None
    _owner_attr = None
    _other_attr = None
    _other_readable = None
    _other_createable = None
    _other_updateable = None
    _other_delete = False
    _all_readable = None
    _all_createable = None
    _all_updateable = None
    _all_delete = False
    _not_readable = list()
    _not_updateable = list()
    _ro_attr = list()

    def _filter_attrs4read(self, attr, is_other=False, is_owner=False, is_admin=False):
        for k in self._not_readable:
            attr.pop(k, None)
        if is_owner or is_admin:
            return attr
        allowed_attr = list()
        if self._all_readable is not None:
            allowed_attr += self._all_readable
        if is_other and self._other_readable is not None:
            allowed_attr += self._other_readable
        for k in list([k for k in attr.keys() if k not in allowed_attr]):
            attr.pop(k, None)
        return attr

    def _filter_attrs4create(self, attr, is_other=False, is_owner=False, is_admin=False):
        attr.pop('_id', None)
        for ro in self._ro_attr:
            attr.pop(ro, None)
        if is_owner or is_admin:
            return attr
        allowed_attr = list()
        if self._all_createable is not None:
            allowed_attr += self._all_createable
        if is_other and self._other_createable is not None:
            allowed_attr += self._other_createable
        for k in list([k for k in attr.keys() if k not in allowed_attr]):
            attr.pop(k, None)
        return attr

    def _filter_attrs4update(self, attr, is_other=False, is_owner=False, is_admin=False):
        attr.pop('_id', None)
        for ro in self._ro_attr:
            attr.pop(ro, None)
        for ro in self._not_updateable:
            attr.pop(ro, None)
        if is_owner or is_admin:
            return attr
        allowed_attr = list()
        if self._all_updateable is not None:
            allowed_attr += self._all_updateable
        if is_other and self._other_updateable is not None:
            allowed_attr += self._other_updateable
        for k in list([k for k in attr.keys() if k not in allowed_attr]):
            attr.pop(k, None)
        return attr

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, element_id=None):
        element = None
        if element_id is not None:
            element = self._element.get(element_id)
        if cherrypy.request.method == 'OPTIONS':
            if element is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST, DELETE'
                cherrypy_cors.preflight(allowed_methods=['GET', 'POST', 'DELETE'])
                return
            else:
                if element['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy_cors.preflight(allowed_methods=['GET', 'PATCH', 'DELETE'])
                return

        is_authorized = False
        is_admin = False
        is_owner = False
        is_other = False
        cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
        if cookie:
            session = self._session_cls.get(cookie.value)
        else:
            session = self._session_cls.get(None)
        if len(session.validate_base()) == 0:
            is_authorized = True
            is_admin = session.admin()

        if not is_authorized and self._all_readable is None and self._all_createable is None and self._all_updateable is None and not self._all_delete:
            cherrypy.response.status = 401
            return {'error': 'not authorized'}
        if is_authorized and not is_admin and self._owner_attr is not None and element is not None:
            if element[self._owner_attr] is not None and element[self._owner_attr] == session['user_id']:
                is_owner = True
        if is_authorized and not is_admin and not is_owner and (element is None or self._other_attr is None or element[self._other_attr]):
            is_other = True

        # GET
        if cherrypy.request.method == 'GET':
            if self._all_readable is None and (not is_authorized or (is_other and self._other_readable is None)):
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element is not None:
                if element['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                return self._filter_attrs4read(element.json(), is_other, is_owner, is_admin)
            else:
                result = list()
                for el in self._element.all():
                    is_owner = False
                    is_other = False
                    if is_authorized and not is_admin and self._owner_attr is not None:
                        if el[self._owner_attr] is not None and el[self._owner_attr] == session['user_id']:
                            is_owner = True
                    if is_authorized and not is_admin and not is_owner and (self._other_attr is None or el[self._other_attr]):
                        is_other = True
                    r = self._filter_attrs4read(el.json(), is_other, is_owner, is_admin)
                    if len(r) > 0:
                        result.append(r)
                return result

        # POST
        elif cherrypy.request.method == 'POST':
            if self._all_createable is None and (not is_authorized or (is_other and self._other_createable is None)):
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element is not None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy.response.status = 405
                return {'error': 'POST not allowed on existing objects'}
            else:
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                elif len(attr) == 0:
                    cherrypy.response.status = 400
                    return {'error': 'data is needed to be submitted'}

                element = self._element(self._filter_attrs4create(attr, is_other, is_owner, is_admin))
                result = element.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result

        # PATCH
        elif cherrypy.request.method == 'PATCH':
            if self._all_updateable is None and (not is_authorized or (is_other and self._other_updateable is None)):
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy.response.status = 405
                return {'error': 'PATCH not allowed on indexes'}
            else:
                if element['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}

                for k, v in self._filter_attrs4update(attr, is_other, is_owner, is_admin).items():
                    element[k] = v
                result = element.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result

        # DELETE
        elif cherrypy.request.method == 'DELETE':
            if not is_admin and not is_owner and not self._all_delete and (not is_authorized or (is_other and not self._other_delete)):
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element is None:
                deleted_ids = list()
                for element in self._element.all():
                    r = element.delete()
                    if 'delete' in r:
                        deleted_ids.append(r['delete'])
                return {'deleted': deleted_ids}
            else:
                if element['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                result = element.delete()
                if 'deleted' not in result:
                    cherrypy.response.status = 400
                return result

        else:
            if element is None:
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
    _all_readable = list()  # List of Settings that are publicly readable
    _admin_writeable = list()  # List of Settings, that are only exposed to and writeable by admins

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
                if el['_id'] is not None and (admin or el['_id'] in self._all_readable):
                    result = el.json()
                    result['ro'] = True if not admin or element_id not in self._admin_writeable else False
                    return result
                else:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
            else:
                result = list()
                for el in self._setting_cls.all():
                    if admin or el['_id'] in self._all_readable:
                        r = el.json()
                        r['ro'] = True if not admin or el['_id'] not in self._admin_writeable else False
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
                if element_id not in self._admin_writeable:
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
                    s = self._session_cls({'user_id': p['_id'], 'complete': False, 'ip': get_client_ip()})
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
                p = self._session_cls._user_cls.get(s['user_id'])
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


class UserEndpointBase(ElementEndpointBase):
    _session_cls = None  # Set this to a child-class of SessionBase in your deriveing class
    _element = None  # Set this to a child-class of UserBase in your deriveing class
    _owner_attr = '_id'
    _other_readable = list(['id', 'login', 'admin'])
    _not_readable = list(['pw'])

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def me(self):
        """
Used to identify the User, that is logged in a session
Just returns the user_id stored in the Session, that is used for the request
        """
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy_cors.preflight(allowed_methods=['GET'])
            return
        elif cherrypy.request.method == 'GET':
            is_authorized = False
            cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
            if cookie:
                session = self._session_cls.get(cookie.value)
                if len(session.validate_base()) == 0:
                    is_authorized = True

            if not is_authorized:
                cherrypy.response.status = 401
                return {'error': 'not authorized'}
            return self._filter_attrs4read(attr=self._element.get(session['user_id']).json(), is_owner=True)
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def password(self, element_id=None):
        """
Used to update the password of a User in a save (encryped) way
Allowed is, that Users are able to update their own password and admins are allowed to update any Users password

element_id is required as part of the URL, as this is the User whos password is updated

the following data have to be transmitted in payload (json dictionary):
    iv: some random generated Initialization Vector, that is fed into AES-CBC algorithm
    pw: the encrypted new password, to be set for the User
        for encryption is used AES in CBC mode, with pkcs7 padding
        the algorithem is fed with the previos mentioned iv and as key the MD5 hashed password, of the User doing the request, is used
    cs: a checksum to validate the correct key is used by the backend to decrypt the new password
        the checksum is a MD5 hash over the following concatenated string: md5-hash(old_password) + iv + encrypted(new_password)
        """
        element = None
        if element_id is not None:
            element = self._element.get(element_id)
        if cherrypy.request.method == 'OPTIONS':
            if element is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS'
                cherrypy_cors.preflight(allowed_methods=[])
                return
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
                cherrypy_cors.preflight(allowed_methods=['PUT'])
                return

        if element['_id'] is None:
            cherrypy.response.status = 404
            return {'error': f'id {element_id} not found'}

        is_authorized = False
        is_admin = False
        is_owner = False
        cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
        if cookie:
            session = self._session_cls.get(cookie.value)
        else:
            session = self._session_cls.get(None)
        if len(session.validate_base()) == 0:
            is_authorized = True
            is_admin = session.admin()
            is_owner = session['user_id'] == element['_id']

        if not is_authorized:
            cherrypy.response.status = 401
            return {'error': 'not authorized'}

        if not is_admin and not is_owner:
            cherrypy.response.status = 403
            return {'error': 'access not allowed'}

        # PUT
        if cherrypy.request.method == 'PUT':
            import hashlib
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            attr = cherrypy.request.json
            if not isinstance(attr, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}
            elif len(attr) == 0:
                cherrypy.response.status = 400
                return {'error': 'data is needed to be submitted'}
            for req_attr in ['iv', 'pw', 'cs']:
                if req_attr not in attr:
                    cherrypy.response.status = 400
                    return {'error': 'missing data'}

            key = hashlib.md5()
            key.update(self._element.get(session['user_id'])['pw'].encode('utf-8'))
            key = key.hexdigest().lower()

            checksum = hashlib.md5()
            checksum.update(key.encode('utf-8'))
            checksum.update(attr['iv'].encode('utf-8'))
            checksum.update(attr['pw'].encode('utf-8'))
            checksum = checksum.hexdigest().lower()
            if not checksum == attr['cs']:
                cherrypy.response.status = 400
                return {'error': 'checksum not valid'}

            key = bytes.fromhex(key)
            iv = bytes.fromhex(attr['iv'])
            pw = bytes.fromhex(attr['pw'])
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pw = unpad(cipher.decrypt(pw), AES.block_size, style='pkcs7')

            element['pw'] = pw.decode('utf-8')
            element.save()

            return {'ok': 'updated password'}
        else:
            if element is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS'
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
