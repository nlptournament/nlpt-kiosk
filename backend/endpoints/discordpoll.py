import cherrypy
import cherrypy_cors
from noapiframe import ElementEndpointBase, docDB
from elements import Session, DiscordPoll


class DiscordPollEndpoint(ElementEndpointBase):
    _session_cls = Session
    _element = DiscordPoll
    _other_readable = list(['id', 'question', 'options', 'channel_id', 'active', 'till_ts'])
    _all_readable = list(['id', 'question', 'options', 'active', 'till_ts'])
    _ro_attr = list(['question', 'options', 'channel_id', 'active', 'till_ts'])

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def filter(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, POST'
            cherrypy_cors.preflight(allowed_methods=['POST'])
            return

        is_authorized = False
        is_admin = False
        is_other = False
        cookie = cherrypy.request.cookie.get(self._session_cls.cookie_name)
        if cookie:
            session = self._session_cls.get(cookie.value)
        else:
            session = self._session_cls.get(None)
        if len(session.validate_base()) == 0:
            is_authorized = True
            is_admin = session.admin()

        if not is_authorized and self._all_readable is None and self._all_createable is None and self._all_updateable is None and not self._all_delete:
            cherrypy.response.status = 401
            return {'error': 'not authorized'}
        if is_authorized and not is_admin:
            is_other = True

        # POST
        if cherrypy.request.method == 'POST':
            from elements import DiscordGuild, DiscordChannel
            if self._all_readable is None and (not is_authorized or (is_other and self._other_readable is None)):
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            attr = cherrypy.request.json
            if not isinstance(attr, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}

            only_active = attr.get('only_active', True)
            guild_id = attr.get('guild_id')
            if guild_id == '':
                guild_id = None
            channel_ids = attr.get('channel_ids')
            if channel_ids is None or not isinstance(channel_ids, list) or len(channel_ids) == 0:
                channel_ids = None

            stages = [{'$match': {}}]
            if only_active:
                stages[0]['$match']['active'] = True
            if channel_ids is not None:
                for channel_id in channel_ids:
                    if DiscordChannel.get(channel_id)['_id'] is None:
                        cherrypy.response.status = 400
                        return {'error': f'invalid channel_id: {channel_id}'}
                else:
                    stages[0]['$match']['channel_id'] = {'$in': channel_ids}
            if guild_id is not None:
                if DiscordGuild.get(guild_id)['_id'] is None:
                    cherrypy.response.status = 400
                    return {'error': f'invalid guild_id: {guild_id}'}
                else:
                    stages.append({'$lookup': {'from': 'DiscordChannel', 'localField': 'channel_id', 'foreignField': '_id', 'as': 'channel'}})
                    stages.append({'$match': {'channel.guild_id': guild_id}})

            result = list()
            for el in docDB.coll('DiscordPoll').aggregate(stages):
                el = self._element(el)
                is_owner = False
                is_other = False
                if is_authorized and not is_admin and self._owner_attr is not None:
                    if el[self._owner_attr] is not None and el[self._owner_attr] == session['user_id']:
                        is_owner = True
                if is_authorized and not is_admin and not is_owner and (self._other_attr is None or el[self._other_attr]):
                    is_other = True
                r = self._filter_attrs4read(el.json(), is_other, is_owner, is_admin)
                if len(r) > 0:
                    result.append(r)

            def sort_func(poll):
                if poll['till_ts'] is not None:
                    return poll['till_ts']
                return 0

            cherrypy.response.headers['Cache-Control'] = 'public,s-maxage=14'
            result.sort(key=sort_func)
            return result

        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, POST'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
