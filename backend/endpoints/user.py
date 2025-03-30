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
