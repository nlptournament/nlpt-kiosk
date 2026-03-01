import cherrypy
import cherrypy_cors
import time
import math
from noapiframe import ElementEndpointBase
from elements import Session, Kiosk, Setting


class KioskEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Kiosk
    _owner_attr = 'added_by_id'
    _other_attr = 'common'
    _other_readable = list(['id', 'name', 'desc', 'added_by_id', 'common', 'timeline_id', 'default_timeline_id'])
    _other_createable = list(['name', 'desc', 'added_by_id', 'common', 'timeline_id', 'default_timeline_id'])
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

            kiosk_id = self._element.id_by_name(element_id, allow_create=Setting.value('new_kiosks'))
            if kiosk_id is None:
                cherrypy.response.status = 405
                return {'error': 'creation of new Kiosk requests is not allowed'}
            else:
                return kiosk_id
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def apply_default(self, element_id=None):
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

            if element_id is None:
                cherrypy.response.status = 404
                return {'error': 'element_id is needed'}
            element = self._element.get(element_id)
            if element['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f'id {element_id} not found'}

            result = element.apply_default()
            if result:
                return True
            else:
                cherrypy.response.status = 500
                return {'error': 'there seems to be no default timeline available for this Kiosk'}
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def apply_timelinetemplate(self, element_id=None):
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
            elif 'template_id' not in attr:
                cherrypy.response.status = 400
                return {'error': "'template_id' needed in data"}

            if element_id is None:
                cherrypy.response.status = 404
                return {'error': 'element_id is needed'}
            element = self._element.get(element_id)
            if element['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f'id {element_id} not found'}

            result = element.apply_timelinetemplate(attr['template_id'])
            if result:
                return True
            else:
                cherrypy.response.status = 500
                return {'error': 'there seems to be no default TimelineTemplate with this id'}
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
