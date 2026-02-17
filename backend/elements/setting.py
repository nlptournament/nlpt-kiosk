from noapiframe.elements import SettingBase


class Setting(SettingBase):
    _defaults = {
        'version':               {'order': 0,  'type': 'str',  'value': None,       'desc': 'Running version of NLPT-Kiosk-Controller'},
        'new_kiosks':            {'order': 1,  'type': 'bool', 'value': True,       'desc': 'enables registration of new Kiosks on Controller'},
        'server_port':           {'order': 10, 'type': 'int',  'value': 8000,       'desc': 'Port the backend should be listening on'},
        'wss_port':              {'order': 11, 'type': 'int',  'value': 8765,       'desc': 'Port the websocket-server should be listening on'},
        's3_host':               {'order': 12, 'type': 'str',  'value': 'minio',    'desc': 'Address of S3 server'},
        's3_port':               {'order': 13, 'type': 'int',  'value': 9000,       'desc': 'Port S3 server is listening on'},
        's3_access_key':         {'order': 14, 'type': 'str',  'value': 'nlptkc',   'desc': 'Username for S3 connection'},
        's3_access_secret':      {'order': 15, 'type': 'str',  'value': 'password', 'desc': 'Password for S3 connection'},
        'anno_src_uri':          {'order': 20, 'type': 'str',  'value': None,       'desc': 'NLPT.online source URI from where the Announcements are pulled'},
        'anno_img_user_id':      {'order': 21, 'type': 'str',  'value': None,       'desc': 'user_id of User who is owning Media for Announcements Screen'},
        'pc_prometheus_uri':     {'order': 30, 'type': 'str',  'value': None,
                                  'desc': 'full URI (with http and port) to prometheus server, providing playercounts'},
        'pc_discord_token':      {'order': 31, 'type': 'str',  'value': None,       'desc': 'token of discord bot, capturing guild playercounts'},
        'tas_uri':               {'order': 40, 'type': 'str',  'value': None,       'desc': 'full URI (with http) where the TAS startpage is reachable'},
        'challonge_user':        {'order': 50, 'type': 'str',  'value': None,       'desc': 'Challonge username used for API connection'},
        'challonge_key':         {'order': 51, 'type': 'str',  'value': None,       'desc': 'Challonge API-key used for connection'},
        'challonge_img_user_id': {'order': 52, 'type': 'str',  'value': None,       'desc': 'user_id of User who is owning Media for Challonge Screens'},
        'mock_anno':             {'order': 90, 'type': 'bool', 'value': False,      'desc': 'if enabled Announcements-Endpoint delivers mockup-data'},
        'mock_pc':               {'order': 91, 'type': 'bool', 'value': False,      'desc': 'if enabled PlayerCounts-Endpoint delivers mockup-data'},
        'mock_tas':              {'order': 92, 'type': 'bool', 'value': False,      'desc': 'if enabled TAS-Endpoint delivers mockup-data'},
        'mock_chal':             {'order': 93, 'type': 'bool', 'value': False,
                                  'desc': 'if enabled Challonge-Endpoints deliver mockup-data (use Tournament-IDs 1 and 2)'}
    }

    def save_post(self):
        if self['_id'] == 'pc_discord_token' and self['value'] is not None:
            from helpers.discord import start_worker
            start_worker()
