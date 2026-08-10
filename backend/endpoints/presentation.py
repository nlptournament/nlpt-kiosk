import cherrypy
import cherrypy_cors
import json
from elements import Session, User


class PresentationEndpoint(object):
    _session_cls = Session

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTION'
            cherrypy_cors.preflight(allowed_methods=[])
            return

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def restart(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy_cors.preflight(allowed_methods=['PUT'])
            return

        # PUT
        elif cherrypy.request.method == 'PUT':
            is_authorized = False
            is_admin = False
            is_presenter = False

            cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
            if cookie:
                session = self._session_cls.get(cookie.value)
            else:
                session = self._session_cls.get(None)
            if len(session.validate_base()) == 0:
                is_authorized = True
                is_admin = session.admin()
                is_presenter = User.get(session['user_id'])['presenter']

            if not is_authorized:
                cherrypy.response.status = 401
                return json.dumps({'error': 'not authorized'}).encode('utf-8')

            if not is_admin and not is_presenter:
                cherrypy.response.status = 403
                return json.dumps({'error': 'access not allowed'}).encode('utf-8')

            from helpers.wss import transmit_presentation_update
            transmit_presentation_update('restart')

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def forward(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy_cors.preflight(allowed_methods=['PUT'])
            return

        # PUT
        elif cherrypy.request.method == 'PUT':
            is_authorized = False
            is_admin = False
            is_presenter = False

            cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
            if cookie:
                session = self._session_cls.get(cookie.value)
            else:
                session = self._session_cls.get(None)
            if len(session.validate_base()) == 0:
                is_authorized = True
                is_admin = session.admin()
                is_presenter = User.get(session['user_id'])['presenter']

            if not is_authorized:
                cherrypy.response.status = 401
                return json.dumps({'error': 'not authorized'}).encode('utf-8')

            if not is_admin and not is_presenter:
                cherrypy.response.status = 403
                return json.dumps({'error': 'access not allowed'}).encode('utf-8')

            from helpers.wss import transmit_presentation_update
            transmit_presentation_update('forward')

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def backward(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy_cors.preflight(allowed_methods=['PUT'])
            return

        # PUT
        elif cherrypy.request.method == 'PUT':
            is_authorized = False
            is_admin = False
            is_presenter = False

            cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
            if cookie:
                session = self._session_cls.get(cookie.value)
            else:
                session = self._session_cls.get(None)
            if len(session.validate_base()) == 0:
                is_authorized = True
                is_admin = session.admin()
                is_presenter = User.get(session['user_id'])['presenter']

            if not is_authorized:
                cherrypy.response.status = 401
                return json.dumps({'error': 'not authorized'}).encode('utf-8')

            if not is_admin and not is_presenter:
                cherrypy.response.status = 403
                return json.dumps({'error': 'access not allowed'}).encode('utf-8')

            from helpers.wss import transmit_presentation_update
            transmit_presentation_update('backward')

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
