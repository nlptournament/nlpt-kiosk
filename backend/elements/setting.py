from noapi.elements import SettingBase


class Setting(SettingBase):
    _defaults = {
        'version':               {'order': 0,  'type': 'str',  'value': None,       'desc': 'Running version of NLPT-Kiosk-Controller'},
        'new_kiosks':            {'order': 1,  'type': 'bool', 'value': True,       'desc': 'enables registration of new Kiosks on Controller'},
        'server_port':           {'order': 2,  'type': 'int',  'value': 8000,       'desc': 'Port the backend should be listening on'},
        'wss_port':              {'order': 3,  'type': 'int',  'value': 8765,       'desc': 'Port the websocket-server should be listening on'},
        's3_host':               {'order': 4,  'type': 'str',  'value': 'minio',    'desc': 'Address of S3 server'},
        's3_port':               {'order': 5,  'type': 'int',  'value': 9000,       'desc': 'Port S3 server is listening on'},
        's3_access_key':         {'order': 6,  'type': 'str',  'value': 'nlptkc',   'desc': 'Username for S3 connection'},
        's3_access_secret':      {'order': 7,  'type': 'str',  'value': 'password', 'desc': 'Password for S3 connection'},
        'anno_src_uri':          {'order': 8,  'type': 'str',  'value': None,       'desc': 'NLPT.online source URI from where the Announcements are pulled'},
        'anno_img_user_id':      {'order': 9,  'type': 'str',  'value': None,       'desc': 'user_id of User who is owning Media for Announcements Screen'},
        'challonge_user':        {'order': 10, 'type': 'str',  'value': None,       'desc': 'Challonge username used for API connection'},
        'challonge_key':         {'order': 11, 'type': 'str',  'value': None,       'desc': 'Challonge API-key used for connection'},
        'challonge_img_user_id': {'order': 12, 'type': 'str',  'value': None,       'desc': 'user_id of User who is owning Media for Challonge Screens'},
        'mock_anno':             {'order': 20, 'type': 'bool', 'value': False,      'desc': 'if enabled Announcements-Endpoint delivers mockup-data'},
        'mock_pc':               {'order': 21, 'type': 'bool', 'value': False,      'desc': 'if enabled PlayerCounts-Endpoint delivers mockup-data'},
        'mock_tas':              {'order': 22, 'type': 'bool', 'value': False,      'desc': 'if enabled TAS-Endpoint delivers mockup-data'},
        'mock_chal':             {'order': 23, 'type': 'bool', 'value': False,
                                  'desc': 'if enabled Challonge-Endpoints deliver mockup-data (use Tournament-IDs 1 and 2)'}
    }
