from noapi.elements import SessionBase
from .user import User


class Session(SessionBase):
    cookie_name = 'NLPTkiosk'
    _user_cls = User
