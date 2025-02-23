import cherrypy
import cherrypy_cors
from noapi import docDB, ElementEndpointBase
from noapi.endpoints import SettingEndpointBase, LoginEndpointBase
from elements import Setting, Session, User
from helpers.versioning import run as versioning_run


class API():
    def __init__(self):
        self.setting = SettingEndpoint()
        self.login = LoginEndpoint()
        self.user = UserEndpoint()


class SettingEndpoint(SettingEndpointBase):
    _setting_cls = Setting
    _session_cls = Session
    user_readable = ['version']
    admin_writeable = ['server_port']


class LoginEndpoint(LoginEndpointBase):
    _session_cls = Session


class UserEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = User


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
