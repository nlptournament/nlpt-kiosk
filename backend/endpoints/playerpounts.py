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
                result = self.mock_data()
            else:
                pass

            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=10'
            result = sorted(result, key=lambda x: (x['game'], x['name']))
            return result

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    def mock_data(self):
        result = list()
        result.append({'name': 'Server3', 'count': 2, 'max': 24, 'game': 'UT2k4'})
        result.append({'name': 'Server2', 'count': 2, 'max': 24, 'game': 'UT2k4'})
        result.append({'name': 'Server1', 'count': 2, 'max': 24, 'game': 'UT2k4'})
        result.append({'name': 'Server1', 'count': 3, 'max': 24, 'game': 'UT3'})
        result.append({'name': 'Server4', 'count': 0, 'max': 24, 'game': 'UT3'})
        result.append({'name': 'Server2', 'count': 3, 'max': 24, 'game': 'UT3'})
        result.append({'name': 'Server3', 'count': 3, 'max': 24, 'game': 'UT3'})
        result.append({'name': 'Server3', 'count': 2, 'max': 32, 'game': 'Battlefield2'})
        result.append({'name': 'Server2', 'count': 3, 'max': 32, 'game': 'Battlefield2'})
        result.append({'name': 'Server1', 'count': 1, 'max': 32, 'game': 'Battlefield2'})
        result.append({'name': 'OpenWorld', 'count': 0, 'max': 20, 'game': 'Minecraft'})
        result.append({'name': 'Tournament', 'count': 10, 'max': 10, 'game': 'Minecraft'})
        result.append({'name': 'Server1', 'count': 0, 'max': 32, 'game': 'CoD4'})
        result.append({'name': 'Server2', 'count': 0, 'max': 32, 'game': 'CoD4'})
        result.append({'name': 'Server3', 'count': 0, 'max': 32, 'game': 'CoD4'})
        result.append({'name': 'Server1', 'count': 2, 'max': 16, 'game': 'CoD2'})
        result.append({'name': 'Server2', 'count': 2, 'max': 16, 'game': 'CoD2'})
        result.append({'name': 'Server3', 'count': 2, 'max': 16, 'game': 'CoD2'})
        result.append({'name': 'NLPT', 'count': 57, 'max': 60, 'game': 'Mordhau'})
        result.append({'name': 'Geheimbasis', 'count': 3, 'max': 4, 'game': 'Left4Dead2'})
        return result
