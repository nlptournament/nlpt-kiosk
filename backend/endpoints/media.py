import cherrypy
import cherrypy_cors
import tempfile
import json
from cherrypy.lib import file_generator
from noapiframe import ElementEndpointBase
from elements import Media, Session


class MediaEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = Media
    _owner_attr = 'user_id'
    _other_attr = 'common'
    _other_readable = list(['id', 'desc', 'src_type', 'src', 'type', 'user_id', 'common'])
    _other_createable = list(['desc', 'src_type', 'src', 'type', 'user_id', 'common'])
    _all_readable = list(['id', 'src_type', 'src', 'type'])

    @cherrypy.expose()
    def s3(self, element_id=None, upload=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'  # json_out() can't be used in this case due to GET returning different content-type
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, POST, GET'
            cherrypy_cors.preflight(allowed_methods=['POST', 'GET'])
            return

        element = self._element.get(element_id)
        if element['_id'] is None:
            cherrypy.response.status = 404
            return json.dumps({'error': f'id {element_id} not found'}).encode('utf-8')

        if not element['src_type'] == 1:
            cherrypy.response.status = 400
            return json.dumps({'error': 'this is not media meant to be stored in internal S3 storage'}).encode('utf-8')

        if cherrypy.request.method == 'POST':
            is_authorized = False
            is_admin = False
            is_owner = False

            cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
            if cookie:
                session = self._session_cls.get(cookie.value)
            else:
                session = self._session_cls.get(None)
            if len(session.validate_base()) == 0:
                is_authorized = True
                is_admin = session.admin()
                if element[self._owner_attr] is not None and element[self._owner_attr] == session['user_id']:
                    is_owner = True

            if not is_authorized:
                cherrypy.response.status = 401
                return json.dumps({'error': 'not authorized'}).encode('utf-8')

            if not is_admin and not is_owner:
                cherrypy.response.status = 403
                return json.dumps({'error': 'access not allowed'}).encode('utf-8')

            if upload is None:
                cherrypy.response.status = 400
                return json.dumps({'error': 'something to be uploaded is needed'}).encode('utf-8')

            size = 0
            with tempfile.TemporaryFile() as tmp_file:
                from helpers.s3 import media_upload
                while True:
                    data = upload.file.read(8192)
                    if not data:
                        break
                    tmp_file.write(data)
                    size += len(data)
                    if size > 104857600:  # 100MB
                        return json.dumps({'error': 'filesize is to big'}).encode('utf-8')
                tmp_file.seek(0)
                if not media_upload(element['_id'], tmp_file):
                    cherrypy.response.status = 400
                    return json.dumps({'error': 'something went wrong saving the file'}).encode('utf-8')
            element['src'] = f"{upload.filename.replace(';', '')};{upload.content_type}"
            element.save()
            return json.dumps({'uploaded': f"{element['src']} to {element['_id']}"}).encode('utf-8')

        elif cherrypy.request.method == 'GET':
            from helpers.s3 import media_get, media_exists
            if not media_exists(element['_id']):
                cherrypy.response.status = 404
                return json.dumps({'error': 'file not found in storage'}).encode('utf-8')

            content = element['src'].split(';')
            if not len(content) == 2:
                cherrypy.response.status = 400
                return json.dumps({'error': "missing metadata! Can't deliver file"}).encode('utf-8')

            cherrypy.response.headers['Content-Type'] = content[1]
            cherrypy.response.headers['Content-Disposition'] = f'inline; filename="{content[0]}"'
            return file_generator(media_get(id=element['_id']))

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, POST, GET'
            cherrypy.response.status = 405
            return json.dumps({'error': 'method not allowed'}).encode('utf-8')
