import cherrypy
import cherrypy_cors
from noapiframe import docDB, ElementEndpointBase
from noapiframe.endpoints import SettingEndpointBase, LoginEndpointBase
from elements import Setting, Session, ScreenTemplate, Screen, ChallongeTournament, ChallongeParticipant, ChallongeMatch, DiscordGuild, DiscordRole
from endpoints import UserEndpoint, TimelineTemplateEndpoint, PresetEndpoint, KioskEndpoint, TimelineEndpoint, MediaEndpoint
from endpoints import AnnouncementsEndpoint, PlayercountsEndpoint, TASEndpoint
from helpers.versioning import run as versioning_run
from helpers.wss import start_server as start_wss_server
from helpers.challonge import start_fetcher as start_challonge_fetcher
from helpers.discord import start_worker as start_discord_worker


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
        self.playercounts = PlayercountsEndpoint()
        self.tas = TASEndpoint()
        self.challongetournament = ChallongeTournamentEndpoint()
        self.challongematch = ChallongeMatchEndpoint()
        self.challongeparticipant = ChallongeParticipantEndpoint()
        self.discordguild = DiscordGuildEndpoint()
        self.discordrole = DiscordRoleEndpoint()


class SettingEndpoint(SettingEndpointBase):
    _setting_cls = Setting
    _session_cls = Session
    _all_readable = ['version', 'wss_port']
    _admin_writeable = [
        'server_port', 'new_kiosks', 'wss_port', 's3_host', 's3_port', 's3_access_key', 's3_access_secret',
        'anno_src_uri', 'anno_img_user_id', 'pc_prometheus_uri', 'discord_bot_token',
        'tas_uri', 'challonge_user', 'challonge_key', 'challonge_img_user_id', 'mock_anno', 'mock_pc', 'mock_tas', 'mock_chal'
    ]


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
    _other_readable = list(['id', 'desc', 'template_id', 'user_id', 'duration', 'till', 'repeat', 'loop', 'variables', 'locked', 'displayed', 'key'])
    _other_createable = list(['desc', 'template_id', 'user_id', 'duration', 'till', 'repeat', 'loop', 'variables'])
    _all_readable = list(['id', 'duration', 'till', 'repeat', 'loop', 'variables', 'key'])


class ChallongeTournamentEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = ChallongeTournament
    _all_readable = list(['id', 'name', 'url', 'state', 'type', 'game', 'available_rounds', 'completed_rounds'])
    if Setting.value('mock_chal'):
        _all_updateable = list(['name', 'url', 'state', 'type', 'game', 'available_rounds', 'completed_rounds'])
    else:
        _ro_attr = list(['name', 'url', 'state', 'type', 'game', 'available_rounds', 'completed_rounds'])


class ChallongeParticipantEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = ChallongeParticipant
    _all_readable = list(['id', 'tournament_id', 'name', 'portrait_id'])
    _ro_attr = list(['tournament_id', 'name', 'portrait_id'])


class ChallongeMatchEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = ChallongeMatch
    _all_readable = list(['id', 'tournament_id', 'state', 'round', 'player1_id', 'player2_id', 'winner_id'])
    _ro_attr = list(['tournament_id', 'state', 'round', 'player1_id', 'player2_id', 'winner_id'])


class DiscordGuildEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = DiscordGuild
    _other_readable = list(['id', 'name'])
    _ro_attr = list(['name'])


class DiscordRoleEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = DiscordRole
    _other_readable = list(['id', 'name', 'guild_id'])
    _ro_attr = list(['name', 'guild_id'])


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
    start_challonge_fetcher()
    start_discord_worker()
    cherrypy.quickstart(API(), '/', conf)
