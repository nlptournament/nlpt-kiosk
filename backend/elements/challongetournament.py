from noapi import ElementBase


class ChallongeTournament(ElementBase):
    """
Cached representation of a Challonge Tournament

name : str
    Tournament name
url : str
    full URL to the tournament on Challonge website as returned by the API variable full_challonge_url
state : int
    integer representing the state the tournament is in
    is translated from the string based variable returned by Challonges API
    can be one of the following values:
        0: unknown (used if the string from Challonges API can't be matched)
        1: pending
        2: underway
        3: complete
type : string
    the kind of tournament (singel elemination, double elemination, ...) returned by the API variable tournament_type
game : string
    the name of the game, that is played on the tournament as returnd by the API variable game_name
completed_rounds : list[int]
    holds all round numbers that are completed, and is just for helping the frontend to not calculate this on every refresh
    a completed round is reached if all matches of this specific round are completed
    """
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, default='', notnone=True),
        url=ElementBase.addAttr(type=str, default='', notnone=True),
        state=ElementBase.addAttr(type=int, default=0, notnone=True),
        type=ElementBase.addAttr(type=str, default='', notnone=True),
        game=ElementBase.addAttr(type=str, default='', notnone=True),
        completed_rounds=ElementBase.addAttr(type=list, default=[], notnone=True)
    )

    translate_state = dict(
        unknown=0,
        pending=1,
        underway=2,
        complete=3
    )

    def validate(self):
        errors = dict()
        if self['state'] not in range(4):
            errors['state'] = {'code': 5, 'desc': 'needs to be one of: [0, 1, 2, 3]'}
        return errors
