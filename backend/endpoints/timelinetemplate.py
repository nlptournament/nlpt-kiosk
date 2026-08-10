import cherrypy
import cherrypy_cors
from noapiframe import ElementEndpointBase
from elements import TimelineTemplate, Session


class TimelineTemplateEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = TimelineTemplate
    _owner_attr = 'user_id'
    _other_readable = list(['id', 'desc', 'user_id', 'screen_ids', 'presentation'])
    _other_createable = list(['desc', 'user_id', 'screen_ids', 'presentation'])

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

            element = self._element.get(element_id)
            if element['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f'id {element_id} not found'}

            return {'updated': element.update_timelines()}
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def import_pdf(self, element_id=None):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy_cors.preflight(allowed_methods=['PUT'])
            return
        elif cherrypy.request.method == 'PUT':
            from elements import Media
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
            elif 'media_id' not in attr:
                cherrypy.response.status = 400
                return {'error': "'media_id' needed in data"}

            element = self._element.get(element_id)
            if element['_id'] is None:
                cherrypy.response.status = 404
                return {'error': f'id {element_id} not found'}

            is_allowed = False
            if session.admin():
                is_allowed = True
            elif session['user_id'] == element[self._owner_attr]:
                is_allowed = True
            elif element[self._other_attr]:
                is_allowed = True

            if not is_allowed:
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}

            pdf_media = Media.get(attr['media_id'])
            if pdf_media['_id'] is None or not pdf_media['type'] == 4 or not pdf_media['src_type'] == 1:
                cherrypy.response.status = 500
                return {'error': 'Media needs to be of type 4 and src_type 1'}
            prefix = attr.get('prefix', 'pdf_importer')
            png_width = int(attr.get('image_width', 1920))

            if element.import_pdf(pdf_media['_id'], prefix, png_width):
                return {'updated': element_id}
            else:
                cherrypy.response.status = 500
                return {'error': 'something went wrong importing pdf'}
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
