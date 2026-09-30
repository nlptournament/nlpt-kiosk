from noapiframe import ElementBase, docDB


class DiscordChannel(ElementBase):
    """
Cached minimalized representation of a Discord Channel

name : str
    name of the channel
guild_id : str
    id of the guild this channel belongs to
    """
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, default=None, notnone=True),
        guild_id=ElementBase.addAttr(type=str, default=None, notnone=True, fk='DiscordGuild'),
    )

    def delete_post(self):
        from elements import DiscordPoll
        for p in [DiscordPoll(p) for p in docDB.search_many('DiscordPoll', {'guild_id': self['_id']})]:
            p.delete()
