import cherrypy
import cherrypy_cors


class TASEndpoint(object):
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTION'
            cherrypy_cors.preflight(allowed_methods=[])
            return

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def challenge_ranks(self):
        from elements import Setting

        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy_cors.preflight(allowed_methods=['GET'])
            return

        # GET
        elif cherrypy.request.method == 'GET':
            result = list()
            if Setting.value('mock_tas'):
                result = self.mock_challenge()
            else:
                pass

            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=10'
            return self.reduce_and_sort(result)

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def global_ranks(self):
        from elements import Setting

        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy_cors.preflight(allowed_methods=['GET'])
            return

        # GET
        elif cherrypy.request.method == 'GET':
            result = list()
            if Setting.value('mock_tas'):
                result = self.mock_global()
            else:
                pass

            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=10'
            return self.reduce_and_sort(result)

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    def reduce_and_sort(self, results):
        results = sorted(results, key=lambda x: (x['rank'], x['player']))
        result = list()
        for r in results:
            if r.get('active', False):
                result.append(r)
                if len(result) >= 20:
                    break
        else:
            for r in results:
                if not r.get('active', False):
                    result.append(r)
                    if len(result) >= 20:
                        break
        result = sorted(result, key=lambda x: (x['rank'], x['player']))
        return result

    def mock_challenge(self):
        result = list()
        result.append({'rank': 1, 'player': 'PlayerName1', 'time': 123456, 'active': True})
        result.append({'rank': 2, 'player': 'PlayerName2', 'time': 124567, 'active': False})
        result.append({'rank': 3, 'player': 'ALongPlayerName', 'time': 124567, 'active': True})
        result.append({'rank': 4, 'player': 'AReallyLongPlayerName', 'time': 124567, 'active': False})
        result.append({'rank': 6, 'player': 'PlayerName3', 'active': False})
        result.append({'rank': 6, 'player': 'PlayerName4', 'time': None, 'active': True})
        return result

    def mock_global(self):
        result = list()
        result.append({'rank': 1, 'player': 'PlayerName1', 'points': 21, 'active': True})
        result.append({'rank': 2, 'player': 'PlayerName2', 'points': 20, 'active': False})
        result.append({'rank': 3, 'player': 'ALongPlayerName', 'points': 19, 'active': True})
        result.append({'rank': 4, 'player': 'AReallyLongPlayerName', 'points': 18, 'active': False})
        result.append({'rank': 5, 'player': 'PlayerName5', 'points': 17, 'active': False})
        result.append({'rank': 6, 'player': 'PlayerName6', 'points': 16, 'active': False})
        result.append({'rank': 7, 'player': 'PlayerName7', 'points': 15, 'active': False})
        result.append({'rank': 16, 'player': 'PlayerName16', 'points': 6, 'active': False})
        result.append({'rank': 8, 'player': 'PlayerName8', 'points': 14, 'active': False})
        result.append({'rank': 9, 'player': 'PlayerName9', 'points': 13, 'active': False})
        result.append({'rank': 10, 'player': 'PlayerName10', 'points': 12, 'active': False})
        result.append({'rank': 11, 'player': 'PlayerName11', 'points': 11, 'active': False})
        result.append({'rank': 12, 'player': 'PlayerName12', 'points': 10, 'active': False})
        result.append({'rank': 13, 'player': 'PlayerName13', 'points': 9, 'active': False})
        result.append({'rank': 14, 'player': 'PlayerName14', 'points': 8, 'active': False})
        result.append({'rank': 15, 'player': 'PlayerName15', 'points': 7, 'active': False})
        result.append({'rank': 17, 'player': 'PlayerName17', 'points': 5, 'active': False})
        result.append({'rank': 18, 'player': 'PlayerName18', 'points': 4, 'active': False})
        result.append({'rank': 19, 'player': 'PlayerName19', 'points': 3, 'active': False})
        result.append({'rank': 20, 'player': 'PlayerName20', 'points': 2, 'active': False})
        result.append({'rank': 21, 'player': 'PlayerName3', 'points': 1, 'active': False})
        result.append({'rank': 22, 'player': 'PlayerName4', 'points': 0, 'active': True})
        return result
