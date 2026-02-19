import cherrypy
import cherrypy_cors


class PlayercountsEndpoint(object):
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        from elements import Setting

        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy_cors.preflight(allowed_methods=['GET'])
            return

        # GET
        elif cherrypy.request.method == 'GET':
            result = list()
            if Setting.value('mock_pc'):
                for s in self.prometheus_mock_data():
                    s['game'] = self.translate_game(s['game'])
                    result.append(s)
            else:
                from helpers.prometheus_connect import PrometheusConnect
                src_uri = Setting.value('pc_prometheus_uri')
                if src_uri is None:
                    cherrypy.response.status = 500
                    return {'error': 'Settings are missing the source for PlayerCounts'}
                try:
                    prom = PrometheusConnect(url=src_uri, disable_ssl=True)
                    tmp = dict()
                    for s in prom.custom_query(query='playercount_num and on (server) up==1'):
                        try:
                            tmp[s['metric']['instance']] = {
                                'name': s['metric']['iname'],
                                'game': self.translate_game(s['metric']['game']),
                                'count': s['value'][-1]
                            }
                        except Exception:
                            pass
                    for s in prom.custom_query(query='playercount_max and on (server) up==1'):
                        if s['metric']['instance'] in tmp:
                            tmp[s['metric']['instance']]['max'] = s['value'][-1]
                    for v in tmp.values():
                        result.append(v)
                except Exception as e:
                    print(f'Error on fetching playercounts: {e}')

            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=9'
            result = sorted(result, key=lambda x: (x['game'], x['name']))
            return result

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def discord(self, guild=None, role=None):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy_cors.preflight(allowed_methods=['GET'])
            return

        # GET
        elif cherrypy.request.method == 'GET':
            from elements import Setting, DiscordMember

            if Setting.value('mock_pc_discord'):
                members = self.__class__.discord_mock_data()
            else:
                members = DiscordMember.all()

            games = dict()
            for member in members:
                if member['game'] is None or member['game'] == '':
                    continue
                if guild is not None and not str(guild) == '' and not str(guild) == member['guild_id']:
                    continue
                if role is not None and not str(role) == '' and str(role) not in member['role_ids']:
                    continue
                if member['game'] not in games:
                    games[member['game']] = 1
                else:
                    games[member['game']] += 1

            result = list()
            for name, count in games.items():
                result.append({'game': name, 'count': count})
            return result

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    def translate_game(self, name):
        translations = {
            'bf2': 'BF 2',
            'ut2k4': 'UT 2004',
            'ut3': 'UT 3',
            'cod2': 'CoD 2',
            'cod4': 'CoD 4',
            'mc': 'Minecraft',
            'gmod': "Garry's Mod"
        }
        return translations.get(name, name)

    def prometheus_mock_data(self):
        result = list()
        result.append({'name': 'Server3', 'count': 2, 'max': 24, 'game': 'ut2k4'})
        result.append({'name': 'Server2', 'count': 2, 'max': 24, 'game': 'ut2k4'})
        result.append({'name': 'Server1', 'count': 2, 'max': 24, 'game': 'ut2k4'})
        result.append({'name': 'Server1', 'count': 19, 'max': 24, 'game': 'ut3'})
        result.append({'name': 'Server4', 'count': 24, 'max': 24, 'game': 'ut3'})
        result.append({'name': 'Server2', 'count': 20, 'max': 24, 'game': 'ut3'})
        result.append({'name': 'Server3', 'count': 23, 'max': 24, 'game': 'ut3'})
        result.append({'name': 'Server3', 'count': 2, 'max': 32, 'game': 'bf2'})
        result.append({'name': 'Server2', 'count': 1, 'max': 32, 'game': 'bf2'})
        result.append({'name': 'Server1', 'count': 0, 'max': 32, 'game': 'bf2'})
        result.append({'name': 'OpenWorld', 'count': 0, 'max': 20, 'game': 'mc'})
        result.append({'name': 'Tournament', 'count': 10, 'max': 10, 'game': 'mc'})
        result.append({'name': 'Server1', 'count': 0, 'max': 32, 'game': 'cod4'})
        result.append({'name': 'Server2', 'count': 0, 'max': 32, 'game': 'cod4'})
        result.append({'name': 'Server3', 'count': 0, 'max': 32, 'game': 'cod4'})
        result.append({'name': 'Server1', 'count': 2, 'max': 16, 'game': 'cod2'})
        result.append({'name': 'Server2', 'count': 2, 'max': 16, 'game': 'cod2'})
        result.append({'name': 'Server3', 'count': 2, 'max': 16, 'game': 'cod2'})
        result.append({'name': 'NLPT', 'count': 57, 'max': 60, 'game': 'Mordhau'})
        result.append({'name': 'NLPT TTT', 'count': 10, 'max': 20, 'game': 'gmod'})
        return result

    @classmethod
    def discord_mock_data(cls):
        from elements import DiscordGuild, DiscordRole

        guilds = [
            {'_id': '1', 'name': 'Guild1'},
            {'_id': '2', 'name': 'Guild2'},
            {'_id': '3', 'name': 'Guild3'},
        ]
        for guild in guilds:
            g = DiscordGuild(guild)
            g.save()

        roles = [
            {'_id': '1', 'guild_id': '1', 'name': 'g1role1'},
            {'_id': '2', 'guild_id': '1', 'name': 'g1role2'},
            {'_id': '3', 'guild_id': '1', 'name': 'g1role3'},
            {'_id': '4', 'guild_id': '2', 'name': 'g2role1'},
            {'_id': '5', 'guild_id': '2', 'name': 'g2role2'},
            {'_id': '6', 'guild_id': '3', 'name': 'g3role1'},
        ]
        for role in roles:
            r = DiscordRole(role)
            r.save()

        members = [
            {'_id': '1', 'guild_id': '1', 'role_ids': ['1'], 'game': 'Game1'},
            {'_id': '2', 'guild_id': '1', 'role_ids': ['1'], 'game': 'Game2'},
            {'_id': '3', 'guild_id': '1', 'role_ids': ['1'], 'game': 'Game3'},
            {'_id': '4', 'guild_id': '1', 'role_ids': ['1', '2'], 'game': 'Game2'},
            {'_id': '5', 'guild_id': '1', 'role_ids': ['1', '2'], 'game': 'Game2'},
            {'_id': '6', 'guild_id': '1', 'role_ids': ['1', '2'], 'game': 'Game3'},
            {'_id': '7', 'guild_id': '1', 'role_ids': ['1', '3'], 'game': 'Game1'},
            {'_id': '8', 'guild_id': '1', 'role_ids': ['1', '3'], 'game': 'Game2'},
            {'_id': '9', 'guild_id': '1', 'role_ids': ['1', '3'], 'game': 'Game2'},
            {'_id': '10', 'guild_id': '1', 'role_ids': ['1', '2', '3'], 'game': 'Game1'},
            {'_id': '11', 'guild_id': '2', 'role_ids': [], 'game': 'Game4'},
            {'_id': '12', 'guild_id': '2', 'role_ids': ['4'], 'game': 'Game4'},
            {'_id': '13', 'guild_id': '2', 'role_ids': ['4'], 'game': 'Game4'},
            {'_id': '14', 'guild_id': '2', 'role_ids': ['4'], 'game': 'Game5'},
            {'_id': '15', 'guild_id': '2', 'role_ids': ['4'], 'game': None},
            {'_id': '16', 'guild_id': '2', 'role_ids': ['5'], 'game': None},
            {'_id': '17', 'guild_id': '2', 'role_ids': ['5'], 'game': None},
            {'_id': '18', 'guild_id': '2', 'role_ids': ['5'], 'game': 'Game4'},
            {'_id': '19', 'guild_id': '2', 'role_ids': ['5'], 'game': 'Game5'},
            {'_id': '20', 'guild_id': '2', 'role_ids': ['4', '5'], 'game': 'Game5'},
            {'_id': '21', 'guild_id': '3', 'role_ids': [], 'game': 'Game6'},
            {'_id': '22', 'guild_id': '3', 'role_ids': [], 'game': 'Game6'},
            {'_id': '23', 'guild_id': '3', 'role_ids': [], 'game': 'Game7'},
            {'_id': '24', 'guild_id': '3', 'role_ids': [], 'game': 'Game3'},
            {'_id': '25', 'guild_id': '3', 'role_ids': [], 'game': 'Game3'},
            {'_id': '26', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game6'},
            {'_id': '27', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game7'},
            {'_id': '28', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game7'},
            {'_id': '29', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game7'},
            {'_id': '30', 'guild_id': '3', 'role_ids': ['6'], 'game': 'Game3'},
        ]
        return members
