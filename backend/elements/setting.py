from noapi.elements import SettingBase


class Setting(SettingBase):
    _defaults = {
        'version':          {'type': 'str', 'value': None,       'desc': 'Running version of NLPT-Kiosk-Controller'},
        'server_port':      {'type': 'int', 'value': 8000,       'desc': 'Port the backend should be listening on'},
        'wss_port':         {'type': 'int', 'value': 8765,       'desc': 'Port the websocket-server should be listening on'},
        's3_host':          {'type': 'str', 'value': 'minio',    'desc': 'Address of S3 server'},
        's3_port':          {'type': 'int', 'value': 9000,       'desc': 'Port S3 server is listening on'},
        's3_access_key':    {'type': 'str', 'value': 'nlptkc',   'desc': 'Username for S3 connection'},
        's3_access_secret': {'type': 'str', 'value': 'password', 'desc': 'Password for S3 connection'}
    }
