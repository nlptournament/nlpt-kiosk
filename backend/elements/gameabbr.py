from noapiframe import ElementBase, docDB


class GameAbbr(ElementBase):
    """
used to abbreviate game-names to be displayed on a Screen

game : str
    game name to be abbreviated
abbr : str
    string the game name is abbreviated to
enabled : bool (default: True)
    wether the abbreviation should take effect or not
    """
    _attrdef = dict(
        game=ElementBase.addAttr(type=str, default='', notnone=True),
        abbr=ElementBase.addAttr(type=str, default='', notnone=True),
        enabled=ElementBase.addAttr(type=bool, default=True, notnone=True)
    )

    @classmethod
    def translate(cls, game_name):
        translation = docDB.search_one(cls.__name__, {'game': game_name, 'enabled': True})
        if translation is None:
            return game_name
        return translation.get('abbr', game_name)

    @classmethod
    def translation_map(cls):
        result = dict()
        for t in docDB.search_many(cls.__name__, {'enabled': True}):
            result[t['game']] = t['abbr']
        return result
