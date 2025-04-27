from noapi.elements import SettingBase


class Setting(SettingBase):
    _defaults = {
        'version':     {'type': 'str', 'value': None, 'desc': 'Running version of NLPT-Kiosk-Controller'},
        'server_port': {'type': 'int', 'value': 8000, 'desc': 'Port the backend should be listening on'},
        'wss_port':    {'type': 'int', 'value': 8765, 'desc': 'Port the websocket-server should be listening on'},
    }
