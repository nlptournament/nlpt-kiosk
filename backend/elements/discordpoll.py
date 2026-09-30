from noapiframe import ElementBase


class DiscordPoll(ElementBase):
    """
Cached minimalized representation of a Discord Poll

question : str
    the question ased in the poll
options : str[]
    possible answer options for question
channel_id : str
    id of the channel this poll belongs to
active : bool
    can the poll still be voted for, is it there force active?
till_ts : int | None
    defines the timestamp when the poll is auto closed/ended
    """
    _attrdef = dict(
        question=ElementBase.addAttr(type=str, default=None, notnone=True),
        options=ElementBase.addAttr(type=list, default=None, notnone=True),
        channel_id=ElementBase.addAttr(type=str, default=None, notnone=True, fk='DiscordChannel'),
        active=ElementBase.addAttr(type=bool, default=True, notnone=True),
        till_ts=ElementBase.addAttr(type=int, default=None, notnone=False),
    )
