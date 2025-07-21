import cherrypy
import cherrypy_cors
from noapiframe.endpoints import UserEndpointBase
from elements import User, Session


class UserEndpoint(UserEndpointBase):
    _session_cls = Session
    _element = User

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def hide_add(self, element_id=None):
        """
        Adds an element_id to the hidden_elements list of User
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
        is_owner = False
        cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
        if cookie:
            session = self._session_cls.get(cookie.value)
        else:
            session = self._session_cls.get(None)
        if len(session.validate_base()) == 0:
            is_authorized = True
            is_owner = session['user_id'] == element['_id']

        if not is_authorized:
            cherrypy.response.status = 401
            return {'error': 'not authorized'}

        if not is_owner:
            cherrypy.response.status = 403
            return {'error': 'access not allowed'}

        # PUT
        if cherrypy.request.method == 'PUT':
            attr = cherrypy.request.json
            if not isinstance(attr, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}
            elif len(attr) == 0:
                cherrypy.response.status = 400
                return {'error': 'data is needed to be submitted'}
            for req_attr in ['element_id']:
                if req_attr not in attr:
                    cherrypy.response.status = 400
                    return {'error': 'missing data'}

            if not attr['element_id'] in element['hidden_elements']:
                element['hidden_elements'].append(attr['element_id'])
                element.save()
                return {'ok': 'added element_id to hidden_elements'}

            return {'ok': 'element_id already in hidden_elements'}
        else:
            if element is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS'
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def hide_del(self, element_id=None):
        """
        Removes an element_id from the hidden_elements list of User
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
        is_owner = False
        cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
        if cookie:
            session = self._session_cls.get(cookie.value)
        else:
            session = self._session_cls.get(None)
        if len(session.validate_base()) == 0:
            is_authorized = True
            is_owner = session['user_id'] == element['_id']

        if not is_authorized:
            cherrypy.response.status = 401
            return {'error': 'not authorized'}

        if not is_owner:
            cherrypy.response.status = 403
            return {'error': 'access not allowed'}

        # PUT
        if cherrypy.request.method == 'PUT':
            attr = cherrypy.request.json
            if not isinstance(attr, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}
            elif len(attr) == 0:
                cherrypy.response.status = 400
                return {'error': 'data is needed to be submitted'}
            for req_attr in ['element_id']:
                if req_attr not in attr:
                    cherrypy.response.status = 400
                    return {'error': 'missing data'}

            if attr['element_id'] in element['hidden_elements']:
                element['hidden_elements'].remove(attr['element_id'])
                element.save()
                return {'ok': 'removed element_id from hidden_elements'}

            return {'ok': 'element_id already removed from hidden_elements'}
        else:
            if element is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS'
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
