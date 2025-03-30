import cherrypy
import cherrypy_cors
from noapi import ElementEndpointBase
from elements import TimelineTemplate, Session


class TimelineTemplateEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = TimelineTemplate
    _owner_attr = 'user_id'
    _other_readable = list(['id', 'desc', 'user_id', 'screen_ids'])
    _other_createable = list(['desc', 'user_id', 'screen_ids'])

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_timelines(self, element_id=None):
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

            tt = TimelineTemplate.get(element_id)
            if tt['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f'id {element_id} not found'}

            return {'updated': tt.update_timelines()}
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
