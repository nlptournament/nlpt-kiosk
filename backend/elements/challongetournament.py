from noapi import ElementBase, docDB


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
    the kind of tournament (single elemination, double elemination, ...) returned by the API variable tournament_type
game : string
    the name of the game, that is played on the tournament as returnd by the API variable game_name
available_rounds : list[int]
    holds all round numbers that are available on this tournamenr, and is just for helping the frontend to not calculate this on every refresh
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
        available_rounds=ElementBase.addAttr(type=list, default=[], notnone=True),
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

    def save_post(self):
        from helpers.wss import transmit_challonge_update
        transmit_challonge_update(self, 'tournament')

    def delete_post(self):
        from elements import ChallongeMatch, ChallongeParticipant
        from helpers.wss import transmit_challonge_delete
        for m in [ChallongeMatch(m) for m in docDB.search_many('ChallongeMatch', {'tournament_id': self['_id']})]:
            m.delete()
        for p in [ChallongeParticipant(p) for p in docDB.search_many('ChallongeParticipant', {'tournament_id': self['_id']})]:
            p.delete()
        transmit_challonge_delete(self, 'tournament')

    def fill_rounds(self):
        from elements import ChallongeMatch
        avail_rounds = list()
        incom_rounds = list()
        for m in [ChallongeMatch(m) for m in docDB.search_many('ChallongeMatch', {'tournament_id': self['_id']})]:
            if m['round'] not in avail_rounds:
                avail_rounds.append(m['round'])
            if not m['state'] == 3 and m['round'] not in incom_rounds:
                incom_rounds.append(m['round'])
        result = list()
        for r in sorted(avail_rounds):
            if r not in incom_rounds:
                result.append(r)
        if not len(avail_rounds) == len(self['available_rounds']):
            self['available_rounds'] = sorted(avail_rounds)
            self['completed_rounds'] = result
            self.save()
        elif not len(result) == len(self['completed_rounds']):
            self['completed_rounds'] = result
            self.save()
