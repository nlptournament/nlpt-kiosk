from noapi import ElementBase


class ChallongeMatch(ElementBase):
    """
Cached representation of a Challonge Match

tournament_id : str
    the tournament this match relates to
state : int
    integer representing the state the match is in
    is translated from the string based variable returned by Challonges API
    can be one of the following values:
        0: unknown (used if the string from Challonges API can't be matched)
        1: pending
        2: open
        3: complete
round : int
    the round this match is part of in the tournament as returnd by the API variable
player1_id : string | None
    the id of the first ChallongeParticipant taking part in this match
player2_id : string | None
    the id of the second ChallongeParticipant taking part in this match
winner_id : string | None
    the id of player1_id or player2_id who won the match
    """
    _attrdef = dict(
        tournament_id=ElementBase.addAttr(type=str, default=None, notnone=True, fk='ChallongeTournament'),
        state=ElementBase.addAttr(type=int, default=0, notnone=True),
        round=ElementBase.addAttr(type=int, default=None, notnone=True),
        player1_id=ElementBase.addAttr(type=str, default=None, notnone=False, fk='ChallongeParticipant'),
        player2_id=ElementBase.addAttr(type=str, default=None, notnone=False, fk='ChallongeParticipant'),
        winner_id=ElementBase.addAttr(type=str, default=None, notnone=False, fk='ChallongeParticipant')
    )

    translate_state = dict(
        unknown=0,
        pending=1,
        open=2,
        complete=3
    )

    def validate(self):
        errors = dict()
        if self['state'] not in range(4):
            errors['state'] = {'code': 5, 'desc': 'needs to be one of: [0, 1, 2, 3]'}
        if self['winner_id'] not in [None, self['player1_id'], self['player2_id']]:
            errors['winner_id'] = {'code': 5, 'desc': f"needs to be one of: [{None}, {self['player1_id']}, {self['player2_id']}]"}
        if self['player2_id'] is not None and self['player2_id'] == self['player1_id']:
            errors['player2_id'] = {'code': 90, 'desc': "can't be equal to player1_id"}
        return errors

    def save_post(self):
        from helpers.wss import transmit_challonge_update
        transmit_challonge_update(self, 'match')

    def delete_post(self):
        from helpers.wss import transmit_challonge_delete
        transmit_challonge_delete(self, 'match')
