import cherrypy
import cherrypy_cors
from noapi import ElementEndpointBase
from elements import Session, Kiosk


class KioskEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Kiosk
    _owner_attr = 'added_by_id'
    _other_attr = 'common'
    _other_readable = list(['id', 'name', 'desc', 'added_by_id', 'common', 'timeline_id'])
    _other_createable = list(['name', 'desc', 'added_by_id', 'common', 'timeline_id'])
    _other_updateable = list(['timeline_id'])
    _all_readable = list(['id', 'name', 'desc', 'timeline_id'])
    _all_createable = list(['name'])

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def my_id(self, element_id=None):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy_cors.preflight(allowed_methods=['PUT'])
            return
        elif cherrypy.request.method == 'PUT':
            if element_id is None:
                cherrypy.response.status = 404
                return {'error': 'name is needed'}

            return self._element.id_by_name(element_id)
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
