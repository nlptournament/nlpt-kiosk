import cherrypy
import cherrypy_cors
from noapi import ElementEndpointBase
from elements import Session, Timeline


class TimelineEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Timeline
    _other_readable = list(['id', 'template_id', 'kiosk_id', 'screen_ids', 'start_pos', 'current_pos', 'start_time', 'locked', 'preset'])
    _other_createable = list(['template_id', 'kiosk_id', 'screen_ids', 'start_pos'])
    _other_updateable = list(['start_pos', 'start_time'])
    _other_delete = True
    _all_readable = list(['id', 'screen_ids', 'start_pos', 'current_pos', 'start_time'])
    _not_updateable = list(['screen_ids'])

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def currentPos(self, element_id=None):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy_cors.preflight(allowed_methods=['PUT'])
            return
        elif cherrypy.request.method == 'PUT':
            from elements import Kiosk
            from noapi import docDB
            data = cherrypy.request.json
            if not isinstance(data, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}

            if 'current_pos' not in data:
                cherrypy.response.status = 400
                return {'error': 'current_pos is missing in data'}

            if 'kiosk_id' not in data:
                cherrypy.response.status = 400
                return {'error': 'kiosk_id is missing in data'}

            t = Timeline.get(element_id)
            if t['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f'id {element_id} not found'}

            k = Kiosk.get(data['kiosk_id'])
            if k['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f"Kiosk with id {data['kiosk_id']} not found"}

            if not k['timeline_id'] == t['_id']:
                cherrypy.response.status = 401
                return {'error': 'not authorized'}

            val = int(int(data['current_pos']) % (len(t['screen_ids']) * 2))
            docDB.update('Timeline', t['_id'], {'$set': {'current_pos': val}})

            return val
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
