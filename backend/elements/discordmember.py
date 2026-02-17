from noapiframe import ElementBase, docDB


class DiscordMember(ElementBase):
    """
Cached minimalized representation of a Discord Member, to hold the currently played game

name : str
    display name of the role
game : str | None
    name of game the player is currently playing, according to discord
    is None, if the player is currently not playing
guild_id : str
    id of the guild this role corresponds to
role_ids : list[str]
    ids of roles the member belongs to within this guild
    """
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, default='', notnone=True),
        game=ElementBase.addAttr(type=str, default=None, notnone=False),
        guild_id=ElementBase.addAttr(type=str, default=None, notnone=True, fk='DiscordGuild'),
        role_ids=ElementBase.addAttr(type=list, default=list(), notnone=True, fk='DiscordRole')
    )

    @classmethod
    def all_for_guild(cls, guild_id):
        result = list()
        for element in docDB.search_many(cls.__name__, {'guild_id': str(guild_id)}):
            result.append(cls(element))
        return result

    def save_pre(self):
        from elements import DiscordRole
        role_ids_to_remove = list()
        for role_id in self['role_ids']:
            if not DiscordRole.exists(role_id):
                role_ids_to_remove.append(role_id)
        for role_id in role_ids_to_remove:
            self['role_ids'].remove(role_id)
