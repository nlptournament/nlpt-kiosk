import cherrypy
import cherrypy_cors
from noapiframe import ElementEndpointBase
from elements import Preset, Session


class PresetEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Preset
    _owner_attr = 'user_id'
    _other_attr = 'common'
    _other_readable = list(['id', 'desc', 'timeline_ids', 'user_id', 'common'])
    _other_createable = list(['desc', 'timeline_ids', 'user_id', 'common'])

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def apply(self, element_id=None):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy_cors.preflight(allowed_methods=['PUT'])
            return
        elif cherrypy.request.method == 'PUT':
            is_authorized = False
            cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
            if cookie:
                session = self._session_cls.get(cookie.value)
                if len(session.validate_base()) == 0:
                    is_authorized = True

            if not is_authorized:
                cherrypy.response.status = 401
                return {'error': 'not authorized'}

            p = Preset.get(element_id)
            if p['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f'id {element_id} not found'}

            return {'created': p.apply()}
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
