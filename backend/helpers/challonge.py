import challonge
from elements import Setting, ChallongeTournament, ChallongeMatch, ChallongeParticipant


def my_fetch_and_parse(method, uri, params_prefix=None, **params):
    """Fetch the given uri and return python dictionary without parsed data-types."""
    response = challonge.api.fetch(method, uri, params_prefix, **params)
    return response.json()


challonge.set_credentials(Setting.value('challonge_user'), Setting.value('challonge_key'))
challonge.api.fetch_and_parse = my_fetch_and_parse


def fetch_tournament(tournament_id):
    at = challonge.tournaments.show(tournament_id)['tournament']
    ct = ChallongeTournament.get(str(tournament_id))

    ct['_id'] = str(at['id'])
    ct['name'] = at['name']
    ct['url'] = at['full_challonge_url']
    ct['state'] = ct.translate_state.get(at['state'], 0)
    ct['type'] = at['tournament_type']
    ct['game'] = at['game_name']
    ct.save(only_on_changes=True)

    fetch_matches(str(tournament_id))
    ct.fill_completed_rounds()


def fetch_matches(tournament_id):
    for am in [am['match'] for am in challonge.matches.index(tournament_id)]:
        cm = ChallongeMatch.get(str(am['id']))

        cm['_id'] = str(am['id'])
        cm['tournament_id'] = str(tournament_id)
        cm['state'] = cm.translate_state.get(am['state'], 0)
        cm['round'] = am['round']
        cm['player1_id'] = None if am['player1_id'] is None else str(am['player1_id'])
        cm['player2_id'] = None if am['player2_id'] is None else str(am['player2_id'])
        cm['winner_id'] = None if am['winner_id'] is None else str(am['winner_id'])

        if cm['player1_id'] is not None and not ChallongeParticipant.exists(cm['player1_id']):
            fetch_participant(tournament_id, cm['player1_id'])
        if cm['player2_id'] is not None and not ChallongeParticipant.exists(cm['player2_id']):
            fetch_participant(tournament_id, cm['player2_id'])

        cm.save(only_on_changes=True)


def fetch_participant(tournament_id, participant_id):
    ap = challonge.participants.show(tournament_id, participant_id)['participant']
    cp = ChallongeParticipant.get(str(participant_id))

    cp['_id'] = str(ap['id'])
    cp['tournament_id'] = str(tournament_id)
    cp['name'] = ap['display_name']
    cp.save(only_on_changes=True)
    if ap['attached_participatable_portrait_url'] is not None:
        cp.fetch_portrait(ap['attached_participatable_portrait_url'], overwrite=True)
