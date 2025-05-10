import cherrypy
import cherrypy_cors
from noapi import ElementEndpointBase
from elements import User, Session


class UserEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = User
    _owner_attr = '_id'
    _other_readable = list(['id', 'login', 'admin'])

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def me(self):
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
            return User.get(session['user_id']).json()
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def password(self, element_id=None):
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
