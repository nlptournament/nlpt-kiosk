from noapi.elements import SettingBase


class Setting(SettingBase):
    _defaults = {
        'server_port': {'type': 'int', 'value': 8000, 'desc': 'Port the backend should be listening on'}
    }
