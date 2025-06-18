import cherrypy
import cherrypy_cors
from noapi import docDB, ElementEndpointBase
from noapi.endpoints import SettingEndpointBase, LoginEndpointBase, UserEndpointBase
from elements import Setting, Session, User, ScreenTemplate, Screen
from endpoints import TimelineTemplateEndpoint, PresetEndpoint, KioskEndpoint, TimelineEndpoint, MediaEndpoint, AnnouncementsEndpoint
from helpers.versioning import run as versioning_run
from helpers.wss import start_server as start_wss_server


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
        self.media = MediaEndpoint()
        self.announcements = AnnouncementsEndpoint()


class SettingEndpoint(SettingEndpointBase):
    _setting_cls = Setting
    _session_cls = Session
    _all_readable = ['version', 'wss_port']
    _admin_writeable = ['server_port', 'wss_port', 's3_host', 's3_port', 's3_access_key', 's3_access_secret', 'anno_src_uri', 'anno_img_user_id']


class LoginEndpoint(LoginEndpointBase):
    _session_cls = Session


class UserEndpoint(UserEndpointBase):
    _session_cls = Session
    _element = User


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


if __name__ == '__main__':
    docDB.wait_for_connection()

    conf = {}
    cherrypy_cors.install()
    cherrypy.config.update({
        'engine.autoreload.on': False,
        'server.socket_host': '0.0.0.0',
        'server.socket_port': Setting.value('server_port'),
        'cors.expose.on': True,
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Access-Control-Allow-Origin', 'http://localhost:4200/'), ('Access-Control-Allow-Credentials', 'true')]})

    versioning_run()
    start_wss_server()
    cherrypy.quickstart(API(), '/', conf)
