import cherrypy
import cherrypy_cors


class PlayercountsEndpoint(object):
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        from elements import Setting, GameAbbr

        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy_cors.preflight(allowed_methods=['GET'])
            return

        # GET
        elif cherrypy.request.method == 'GET':
            result = list()
            if Setting.value('mock_pc'):
                game_translation = GameAbbr.translation_map()
                for s in self.prometheus_mock_data():
                    s['game'] = game_translation.get(s['game'], s['game'])
                    result.append(s)
            else:
                from helpers.prometheus_connect import PrometheusConnect
                src_uri = Setting.value('pc_prometheus_uri')
                if src_uri is None:
                    cherrypy.response.status = 500
                    return {'error': 'Settings are missing the source for PlayerCounts'}
                try:
                    game_translation = GameAbbr.translation_map()
                    prom = PrometheusConnect(url=src_uri, disable_ssl=True)
                    tmp = dict()
                    for s in prom.custom_query(query='playercount_num and on (server) up==1'):
                        try:
                            tmp[s['metric']['instance']] = {
                                'name': s['metric']['iname'],
                                'game': game_translation.get(s['metric']['game'], s['metric']['game']),
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
            return self.__class__.discord_counts(guild, role)

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

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
    def discord_counts(cls, guild=None, role=None):
        from elements import DiscordMember, GameAbbr

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

        game_translation = GameAbbr.translation_map()
        result = list()
        for name, count in games.items():
            result.append({'game': game_translation.get(name, name), 'count': count})
        return result
