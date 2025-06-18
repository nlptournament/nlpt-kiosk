import cherrypy
import cherrypy_cors
import requests
import tempfile
from datetime import datetime, timedelta


class AnnouncementsEndpoint(object):
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        from elements import Setting, User, Media
        from helpers.s3 import media_upload

        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy_cors.preflight(allowed_methods=['GET'])
            return

        # GET
        elif cherrypy.request.method == 'GET':
            result = list()
            if Setting.value('mock_anno'):
                result = self.mock_data()
            else:
                src_uri = Setting.value('anno_src_uri')
                media_user = User.get(Setting.value('anno_img_user_id'))
                if src_uri is None:
                    cherrypy.response.status = 500
                    return {'error': 'Settings are missing the source for Announcements'}
                if media_user['_id'] is None:
                    cherrypy.response.status = 500
                    return {'error': 'Settings are missing Media-Owner User'}

                try:
                    for a in requests.get(src_uri).json()['data']:
                        if a['enabled']:
                            anno = dict()
                            anno['id'] = a['id']
                            anno['layout'] = a['layout'] if a['layout'] in ['ffa', 'danger', 'default'] else 'default'
                            anno['title'] = a['title']
                            anno['msg'] = a['message']
                            anno['target'] = a['start_at_unix'] if a['start_at_unix'] > 0 else None
                            if a['image_path'] is None:
                                anno['img'] = None
                            elif (media_id := Media.get_by_filename(a['image_path'])['_id']) is not None:
                                anno['img'] = media_id
                            else:
                                media = Media({'src_type': 1, 'user_id': media_user['_id'], 'common': False, 'type': 0})
                                media.save()
                                img = requests.get(a['image_url'])
                                with tempfile.TemporaryFile() as tmp_file:
                                    tmp_file.write(img.content)
                                    tmp_file.seek(0)
                                    media_upload(media['_id'], tmp_file)
                                media['src'] = f"{a['image_path'].replace(';', '')};{img.headers.get('Content-Type')}"
                                media.save()
                                anno['img'] = media['_id']
                            result.append(anno)
                except Exception:
                    pass

            def sort_func(anno):
                r = 0
                if anno['layout'] == 'danger':
                    r -= 32000000 * 2
                elif anno['layout'] == 'default':
                    r -= 32000000
                if anno['target'] is not None:
                    r += int(datetime.fromtimestamp(anno['target']).replace(year=1970).timestamp())
                r += anno['id']
                return r

            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=15'
            result.sort(key=sort_func)
            return result

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}

    def mock_data(self):
        result = list()
        anno = {'id': 1, 'layout': 'default', 'title': '', 'msg': 'Eine Info', 'target': None, 'img': None}
        result.append(anno)
        anno = {'id': 2, 'layout': 'danger', 'title': 'Pommes fassen!', 'msg': '', 'target': None, 'img': None}
        result.append(anno)
        anno = {'id': 3, 'layout': 'ffa', 'title': 'Bloons TD', 'msg': 'In zwei stunden gehts los', 'target': None, 'img': None}
        anno['target'] = int((datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)).timestamp())
        result.append(anno)
        anno = {'id': 4, 'layout': 'default', 'title': 'Info', 'msg': 'noch ne Info, mit mehr Inhalt', 'target': None, 'img': None}
        result.append(anno)
        anno = {'id': 5, 'layout': 'ffa', 'title': 'FallGuys', 'msg': 'zur vollen Stunde FallGuys', 'target': None, 'img': None}
        anno['target'] = int((datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).timestamp())
        result.append(anno)
        return result
