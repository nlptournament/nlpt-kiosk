from noapiframe import ElementBase, docDB


class DiscordRole(ElementBase):
    """
Cached minimalized representation of a Discord Role

name : str
    display name of the role
guild_id : str
    id of the guild this role corresponds to
    """
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, default=None, notnone=True),
        guild_id=ElementBase.addAttr(type=str, default=None, notnone=True, fk='DiscordGuild')
    )

    def delete_post(self):
        from elements import DiscordMember
        for m in [DiscordMember(m) for m in docDB.search_many('DiscordMember', {'role_ids': self['_id']})]:
            m['role_ids'].remove(self['_id'])
            m.save()
