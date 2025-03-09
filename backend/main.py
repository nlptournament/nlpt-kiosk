import cherrypy
import cherrypy_cors
from noapi import docDB, ElementEndpointBase
from noapi.endpoints import SettingEndpointBase, LoginEndpointBase
from elements import Setting, Session, User, ScreenTemplate, Screen, TimelineTemplate, Timeline, Kiosk, Preset
from helpers.versioning import run as versioning_run


class API():
    def __init__(self):
        self.setting = SettingEndpoint()
        self.login = LoginEndpoint()
        self.user = UserEndpoint()
        self.screentemplate = ScreenTemplateEndpoint()
        self.screen = ScreenEndpoint()
        self.timelinetemplate = TimelineTemplateEndpoint()
        self.timeline = TimelineEndpoint()
        self.kiosk = KioskEndpoint()
        self.preset = PresetEndpoint()


class SettingEndpoint(SettingEndpointBase):
    _setting_cls = Setting
    _session_cls = Session
    _all_readable = ['version']
    _admin_writeable = ['server_port']


class LoginEndpoint(LoginEndpointBase):
    _session_cls = Session


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


class ScreenTemplateEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = ScreenTemplate
    _other_readable = list(['id', 'key', 'name', 'desc', 'endless', 'duration', 'variables_def'])
    _ro_attr = list(['key', 'name', 'desc', 'endless', 'duration', 'variables_def'])


class ScreenEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Screen
    _owner_attr = 'user_id'
    _other_readable = list(['id', 'desc', 'template_id', 'user_id', 'duration', 'repeat', 'loop', 'variables', 'locked', 'key'])
    _other_createable = list(['desc', 'template_id', 'user_id', 'duration', 'repeat', 'loop', 'variables'])
    _all_readable = list(['id', 'duration', 'repeat', 'loop', 'variables', 'key'])


class TimelineTemplateEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = TimelineTemplate
    _owner_attr = 'user_id'
    _other_readable = list(['id', 'desc', 'user_id', 'screen_ids'])
    _other_createable = list(['desc', 'user_id', 'screen_ids'])


class TimelineEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Timeline
    _other_readable = list(['id', 'template_id', 'kiosk_id', 'screen_ids', 'start_pos', 'current_pos', 'locked', 'preset'])
    _other_createable = list(['template_id', 'kiosk_id', 'start_pos'])
    _other_updateable = list(['start_pos'])
    _other_delete = True
    _all_readable = list(['id', 'screen_ids', 'start_pos', 'current_pos'])
    _all_updateable = list(['current_pos'])
    _ro_attr = list(['screen_ids'])


class KioskEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Kiosk
    _owner_attr = 'added_by_id'
    _other_attr = 'common'
    _other_readable = list(['id', 'name', 'desc', 'added_by_id', 'common', 'timeline_id'])
    _other_createable = list(['name', 'desc', 'added_by_id', 'common', 'timeline_id'])
    _other_updateable = list(['timeline_id'])
    _all_readable = list(['id', 'name', 'timeline_id'])
    _all_createable = list(['name'])


class PresetEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Preset
    _owner_attr = 'user_id'
    _other_attr = 'common'
    _other_readable = list(['id', 'desc', 'timeline_ids', 'user_id', 'common'])
    _other_createable = list(['desc', 'timeline_ids', 'user_id', 'common'])


if __name__ == '__main__':
    conf = {}
    listen_port = Setting.value('server_port')
    cherrypy_cors.install()
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': listen_port,
        'cors.expose.on': True,
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Access-Control-Allow-Origin', 'http://localhost:4200/'), ('Access-Control-Allow-Credentials', 'true')]})

    docDB.wait_for_connection()
    versioning_run()
    cherrypy.quickstart(API(), '/', conf)
