import time
import challonge
from multiprocessing import Process
from elements import Setting, ChallongeTournament, ChallongeMatch, ChallongeParticipant


fetcher_process = None


def my_fetch_and_parse(method, uri, params_prefix=None, **params):
    """Fetch the given uri and return python dictionary without parsed data-types."""
    response = challonge.api.fetch(method, uri, params_prefix, **params)
    return response.json()


challonge.set_credentials(Setting.value('challonge_user'), Setting.value('challonge_key'))
challonge.api.fetch_and_parse = my_fetch_and_parse


def start_fetcher():
    global fetcher_process
    if fetcher_process is None:
        fetcher_process = Process(target=fetcher, daemon=True)
        fetcher_process.start()


def fetcher():
    from noapi import docDB
    from elements import ScreenTemplate, Screen
    templates = list()
    for st in ScreenTemplate.all():
        if st['key'].startswith('challonge'):
            templates.append(st['_id'])
    loop_no = 0
    while True:
        loop_no %= 6
        tournaments = list()
        for template_id in templates:
            for s in [Screen(s) for s in docDB.search_many('Screen', {'template_id': template_id})]:
                # if loop_no = 0 fetch all
                # else only fetch active
                if loop_no == 0 or s.locked():
                    for k in ['tournament_id']:
                        if k in s['variables'] and s['variables'][k] not in tournaments:
                            tournaments.append(s['variables'][k])
        for tournament in tournaments:
            try:
                fetch_tournament(tournament)
            except Exception as e:
                print(f'error on fetching challonge tournament {tournament}: {e}')
        loop_no += 1
        time.sleep(10)


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
    ct.fill_rounds()


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
    if cp['name'].endswith(' (invitation pending)'):
        cp['name'] = cp['name'].replace(' (invitation pending)', '')
    cp.save(only_on_changes=True)
    if ap['attached_participatable_portrait_url'] is not None:
        cp.fetch_portrait(ap['attached_participatable_portrait_url'], overwrite=True)
