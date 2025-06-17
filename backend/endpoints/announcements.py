import cherrypy
import cherrypy_cors
import requests
import tempfile


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
            src_uri = Setting.value('anno_src_uri')
            media_user = User.get(Setting.value('anno_img_user_id'))
            if src_uri is None:
                cherrypy.response.status = 500
                return {'error': 'Settings are missing the source for Announcements'}
            if media_user['_id'] is None:
                cherrypy.response.status = 500
                return {'error': 'Settings are missing Media-Owner User'}

            result = list()
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

            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=15'
            return result

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
