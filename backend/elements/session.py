from noapi.elements import SessionBase
from .user import User


class Session(SessionBase):
    cookie_name = 'NLPT-Kiosk-Controller'
    _user_cls = User
