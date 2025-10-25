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
                for s in self.mock_data():
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

    def mock_data(self):
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
