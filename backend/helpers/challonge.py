import time
import json
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
    if Setting.value('mock_chal'):
        mock_data()
        return

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
                    for k in ['tournament_id', 'tournament1_id', 'tournament2_id']:
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


def mock_data():
    t1 = ChallongeTournament({'_id': '1', 'name': 'DevTest1', 'url': 'https://challonge.com/nz456pb9',
                              'state': 2, 'type': 'double elimination', 'game': 'TrackMania Nations Forever'})
    t1.save()
    t2 = ChallongeTournament({'_id': '2', 'name': 'Main Contest Shooter 1v1', 'url': 'https://challonge.com/d5zad7t9',
                              'state': 3, 'type': 'double elimination', 'game': 'Splitgate'})
    t2.save()

    for pd, url in json.loads("""
[[{"_id": "265778079", "tournament_id": "1", "name": "TestUse3"}, null],
[{"_id": "265683251", "tournament_id": "1", "name": "RUSGOR"},
"https://s3.amazonaws.com/challonge_app/users/images/003/972/467/xlarge/Link_as_Raven_with_bg.png"],
[{"_id": "265679262", "tournament_id": "1", "name": "nijovanostow"},
"https://secure.gravatar.com/avatar/a587029111ea58f0b6a683c16c30a550?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "265718245", "tournament_id": "1", "name":"grassi_4"},
"https://secure.gravatar.com/avatar/26822e70f7a53dfe035c454a66b6fdc1?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "265716687", "tournament_id": "1", "name": "Saloni223"}, "https://s3.amazonaws.com/challonge_app/users/images/005/162/188/xlarge/S.png"],
[{"_id": "265778068", "tournament_id": "1", "name": "TestUser2"}, null],
[{"_id": "265715087", "tournament_id": "1", "name": "Neitmaere"},
"https://s3.amazonaws.com/challonge_app/users/images/003/960/283/xlarge/me_as_anime_low.png"],
[{"_id": "265778065", "tournament_id": "1", "name": "TestUser1"}, null],
[{"_id": "243577387", "tournament_id": "2", "name": "Rusky2707"},
"https://secure.gravatar.com/avatar/fe2e549d80b6e409d31e7cf714cf494b?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577396", "tournament_id": "2", "name": "Brainstorm_TM"}, "https://s3.amazonaws.com/challonge_app/users/images/005/162/275/xlarge/BMW_.png"],
[{"_id": "243577390", "tournament_id": "2", "name": "TheMohawk92"},
"https://secure.gravatar.com/avatar/0b45de0e038f0faddad46c5012798fd8?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577388", "tournament_id": "2", "name": "nightaR"},
"https://secure.gravatar.com/avatar/c8d033a09f0b943547dcdba7f34a06ce?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577386", "tournament_id": "2", "name": "Krischaan3"},
"https://secure.gravatar.com/avatar/b55d09e958da6259c865a2e801a1f056?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "244083461", "tournament_id": "2", "name": "TLA"}, null],
[{"_id": "245303640", "tournament_id": "2", "name": "CaFier"}, null],
[{"_id": "243577392", "tournament_id": "2", "name": "LeCarry"},
"https://secure.gravatar.com/avatar/622a9881f5339d31a6ee64d48a97cfb5?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577397", "tournament_id": "2", "name": "Airic"}, null],
[{"_id": "243577393", "tournament_id": "2", "name": "Msei"},
"https://secure.gravatar.com/avatar/4f9ff2f1f02c2f06cbacfa7719a7d6c0?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243580122", "tournament_id": "2", "name": "mayorx8"},
"https://secure.gravatar.com/avatar/4190974a4933fee2764db0be33180fa2?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "245446855", "tournament_id": "2", "name": "Ludwigsfeld"},
"https://secure.gravatar.com/avatar/e2bfe0a817d476ec5f3dbc835a397790?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577391", "tournament_id": "2", "name": "Sorbert01"},
"https://secure.gravatar.com/avatar/59ed6f3b9ba65617b3e0c79efa81d6f0?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577395", "tournament_id": "2", "name": "Redux"},
"https://secure.gravatar.com/avatar/956d309d52e39864a9c54747d79f86d3?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577394", "tournament_id": "2", "name": "V1kVorteX"},
"https://secure.gravatar.com/avatar/2081e412ff51dece1482bf54f888833e?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"],
[{"_id": "243577389", "tournament_id": "2", "name": "LogiJ\\u00f6w"},
"https://secure.gravatar.com/avatar/e9ccef2484f4cf604dbca9ed3d468b88?r=r&s=96&d=https://s3.amazonaws.com/challonge_app/misc/challonge_fireball_gray.png"]]
    """):
        if not ChallongeParticipant.exists(pd['_id']):
            p = ChallongeParticipant(pd)
            p.save()
            if url is not None:
                p.fetch_portrait(url)

    for m in [
            {'_id': '416941306', 'tournament_id': '1', 'state': 3, 'round': 1, 'player1_id': '265778079', 'player2_id': '265683251', 'winner_id': '265683251'},
            {'_id': '416941307', 'tournament_id': '1', 'state': 2, 'round': 1, 'player1_id': '265679262', 'player2_id': '265718245', 'winner_id': None},
            {'_id': '416941308', 'tournament_id': '1', 'state': 2, 'round': 1, 'player1_id': '265716687', 'player2_id': '265778068', 'winner_id': None},
            {'_id': '416941309', 'tournament_id': '1', 'state': 2, 'round': 1, 'player1_id': '265715087', 'player2_id': '265778065', 'winner_id': None},
            {'_id': '416941310', 'tournament_id': '1', 'state': 1, 'round': 2, 'player1_id': '265683251', 'player2_id': None, 'winner_id': None},
            {'_id': '416941311', 'tournament_id': '1', 'state': 1, 'round': 2, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941312', 'tournament_id': '1', 'state': 1, 'round': 3, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941313', 'tournament_id': '1', 'state': 1, 'round': -1, 'player1_id': '265778079', 'player2_id': None, 'winner_id': None},
            {'_id': '416941314', 'tournament_id': '1', 'state': 1, 'round': -1, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941315', 'tournament_id': '1', 'state': 1, 'round': -2, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941316', 'tournament_id': '1', 'state': 1, 'round': -2, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941317', 'tournament_id': '1', 'state': 1, 'round': -3, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941318', 'tournament_id': '1', 'state': 1, 'round': -4, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941319', 'tournament_id': '1', 'state': 1, 'round': 4, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '416941320', 'tournament_id': '1', 'state': 1, 'round': 4, 'player1_id': None, 'player2_id': None, 'winner_id': None},
            {'_id': '389575087', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '243577387', 'player2_id': '243577396', 'winner_id': '243577387'},
            {'_id': '389575088', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '243577390', 'player2_id': '243577388', 'winner_id': '243577388'},
            {'_id': '389575089', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '243577386', 'player2_id': '244083461', 'winner_id': '244083461'},
            {'_id': '389575090', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '245303640', 'player2_id': '243577392', 'winner_id': '243577392'},
            {'_id': '389575091', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '243577397', 'player2_id': '243577393', 'winner_id': '243577393'},
            {'_id': '389575092', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '243580122', 'player2_id': '245446855', 'winner_id': '243580122'},
            {'_id': '389575093', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '243577391', 'player2_id': '243577395', 'winner_id': '243577395'},
            {'_id': '389575094', 'tournament_id': '2', 'state': 3, 'round': 1, 'player1_id': '243577394', 'player2_id': '243577389', 'winner_id': '243577389'},
            {'_id': '389575095', 'tournament_id': '2', 'state': 3, 'round': 2, 'player1_id': '243577387', 'player2_id': '243577388', 'winner_id': '243577388'},
            {'_id': '389575096', 'tournament_id': '2', 'state': 3, 'round': 2, 'player1_id': '244083461', 'player2_id': '243577392', 'winner_id': '243577392'},
            {'_id': '389575097', 'tournament_id': '2', 'state': 3, 'round': 2, 'player1_id': '243577393', 'player2_id': '243580122', 'winner_id': '243577393'},
            {'_id': '389575098', 'tournament_id': '2', 'state': 3, 'round': 2, 'player1_id': '243577395', 'player2_id': '243577389', 'winner_id': '243577395'},
            {'_id': '389575099', 'tournament_id': '2', 'state': 3, 'round': 3, 'player1_id': '243577388', 'player2_id': '243577392', 'winner_id': '243577388'},
            {'_id': '389575100', 'tournament_id': '2', 'state': 3, 'round': 3, 'player1_id': '243577393', 'player2_id': '243577395', 'winner_id': '243577393'},
            {'_id': '389575101', 'tournament_id': '2', 'state': 3, 'round': 4, 'player1_id': '243577388', 'player2_id': '243577393', 'winner_id': '243577393'},
            {'_id': '389575102', 'tournament_id': '2', 'state': 3, 'round': -1, 'player1_id': '243577396', 'player2_id': '243577390', 'winner_id': '243577390'},
            {'_id': '389575103', 'tournament_id': '2', 'state': 3, 'round': -1, 'player1_id': '243577386', 'player2_id': '245303640', 'winner_id': '245303640'},
            {'_id': '389575104', 'tournament_id': '2', 'state': 3, 'round': -1, 'player1_id': '243577397', 'player2_id': '245446855', 'winner_id': '243577397'},
            {'_id': '389575105', 'tournament_id': '2', 'state': 3, 'round': -1, 'player1_id': '243577391', 'player2_id': '243577394', 'winner_id': '243577394'},
            {'_id': '389575106', 'tournament_id': '2', 'state': 3, 'round': -2, 'player1_id': '243577389', 'player2_id': '243577390', 'winner_id': '243577390'},
            {'_id': '389575107', 'tournament_id': '2', 'state': 3, 'round': -2, 'player1_id': '243580122', 'player2_id': '245303640', 'winner_id': '243580122'},
            {'_id': '389575108', 'tournament_id': '2', 'state': 3, 'round': -2, 'player1_id': '244083461', 'player2_id': '243577397', 'winner_id': '243577397'},
            {'_id': '389575109', 'tournament_id': '2', 'state': 3, 'round': -2, 'player1_id': '243577387', 'player2_id': '243577394', 'winner_id': '243577387'},
            {'_id': '389575110', 'tournament_id': '2', 'state': 3, 'round': -3, 'player1_id': '243577390', 'player2_id': '243580122', 'winner_id': '243577390'},
            {'_id': '389575111', 'tournament_id': '2', 'state': 3, 'round': -3, 'player1_id': '243577397', 'player2_id': '243577387', 'winner_id': '243577387'},
            {'_id': '389575112', 'tournament_id': '2', 'state': 3, 'round': -4, 'player1_id': '243577392', 'player2_id': '243577390', 'winner_id': '243577392'},
            {'_id': '389575113', 'tournament_id': '2', 'state': 3, 'round': -4, 'player1_id': '243577395', 'player2_id': '243577387', 'winner_id': '243577395'},
            {'_id': '389575114', 'tournament_id': '2', 'state': 3, 'round': -5, 'player1_id': '243577392', 'player2_id': '243577395', 'winner_id': '243577395'},
            {'_id': '389575115', 'tournament_id': '2', 'state': 3, 'round': -6, 'player1_id': '243577388', 'player2_id': '243577395', 'winner_id': '243577395'},
            {'_id': '389575116', 'tournament_id': '2', 'state': 3, 'round': 5, 'player1_id': '243577393', 'player2_id': '243577395', 'winner_id': '243577395'},
            {'_id': '389575117', 'tournament_id': '2', 'state': 3, 'round': 5, 'player1_id': '243577395', 'player2_id': '243577393', 'winner_id': '243577395'}
            ]:
        if not ChallongeMatch.exists(m['_id']):
            ChallongeMatch(m).save()

    t1.fill_rounds()
    t2.fill_rounds()
