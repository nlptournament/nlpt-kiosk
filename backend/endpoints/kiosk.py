import cherrypy
import cherrypy_cors
import time
import math
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

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def synced_apply(self, element_id=None):
        from elements import Timeline
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

            attr = cherrypy.request.json
            if not isinstance(attr, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}
            elif len(attr) == 0:
                cherrypy.response.status = 400
                return {'error': 'data is needed to be submitted'}

            data = list()
            for kiosk_id, timeline_id in attr.items():
                k = self._element.get(kiosk_id)
                if k['_id'] is None:
                    cherrypy.response.status = 400
                    return {'error': f'could not find Kiosk with id {kiosk_id}'}
                t = Timeline.get(timeline_id)
                if t['_id'] is None:
                    cherrypy.response.status = 400
                    return {'error': f'could not find Timeline with id {timeline_id}'}
                data.append((k, t))

            is_allowed = False
            if session.admin():
                is_allowed = True
            else:
                for k, t in data:
                    if not k[self._other_attr]:
                        is_allowed = False
                        break
                else:
                    is_allowed = True

            if not is_allowed:
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}

            target = math.ceil(time.time()) + 1
            for k, t in data:
                t['start_time'] = target
                t.save()
                k['timeline_id'] = t['_id']
                k.save()

            return attr
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
