from noapi import ElementBase


class ChallongeParticipant(ElementBase):
    """
Cached representation of a Challonge Participant

tournament_id : str
    the tournament this participant relates to
name : string
    the name of the participant as returned by the API variable display_name
portrait_id : string | None
    Media element containing the portrait or avatar of the participant, is taken from the API variable attached_participatable_portrait_url
    """
    _attrdef = dict(
        tournament_id=ElementBase.addAttr(type=str, default=None, notnone=True, fk='ChallongeTournament'),
        name=ElementBase.addAttr(type=str, default=None, notnone=True),
        portrait_id=ElementBase.addAttr(type=str, default=None, notnone=False, fk='Media')
    )
