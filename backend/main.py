import cherrypy
import cherrypy_cors
from noapi import docDB, ElementEndpointBase
from noapi.endpoints import SettingEndpointBase, LoginEndpointBase
from elements import Setting, Session, ScreenTemplate, Screen, Timeline, Kiosk
from endpoints import UserEndpoint, TimelineTemplateEndpoint, PresetEndpoint
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


class TimelineEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Timeline
    _other_readable = list(['id', 'template_id', 'kiosk_id', 'screen_ids', 'start_pos', 'current_pos', 'locked', 'preset'])
    _other_createable = list(['template_id', 'kiosk_id', 'screen_ids', 'start_pos'])
    _other_updateable = list(['start_pos'])
    _other_delete = True
    _all_readable = list(['id', 'screen_ids', 'start_pos', 'current_pos'])
    _all_updateable = list(['current_pos'])
    _not_updateable = list(['screen_ids'])


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
