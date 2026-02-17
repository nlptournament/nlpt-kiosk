from noapiframe import ElementBase, docDB


class DiscordGuild(ElementBase):
    """
Cached minimalized representation of a Discord Guild

name : str
    name of the guild
    """
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, default=None, notnone=True)
    )

    def delete_post(self):
        from elements import DiscordMember, DiscordRole
        for m in [DiscordMember(m) for m in docDB.search_many('DiscordMember', {'guild_id': self['_id']})]:
            m.delete()
        for r in [DiscordRole(r) for r in docDB.search_many('DiscordRole', {'guild_id': self['_id']})]:
            r.delete()
