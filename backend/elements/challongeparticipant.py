from noapiframe import ElementBase, docDB


class ChallongeParticipant(ElementBase):
    """
Cached representation of a Challonge Participant

tournament_id : str
    the tournament this participant relates to
name : string
    the name of the participant as returned by the API variable display_name
portrait_id : string | None
    Media element containing the portrait or avatar of the participant, is taken from the API variable attached_participatable_portrait_url
    """
    _attrdef = dict(
        tournament_id=ElementBase.addAttr(type=str, default=None, notnone=True, fk='ChallongeTournament'),
        name=ElementBase.addAttr(type=str, default=None, notnone=True),
        portrait_id=ElementBase.addAttr(type=str, default=None, notnone=False, fk='Media')
    )

    def save_post(self):
        from helpers.wss import transmit_challonge_update
        transmit_challonge_update(self, 'participant')

    def delete_post(self):
        from elements import ChallongeMatch, Media
        from helpers.wss import transmit_challonge_delete
        for m in [ChallongeMatch(m) for m in docDB.search_many('ChallongeMatch', {'winner_id': self['_id']})]:
            m['winner_id'] = None
            if m['player1_id'] == self['_id']:
                m['player1_id'] = None
            if m['player2_id'] == self['_id']:
                m['player2_id'] = None
            m.save()
        for m in [ChallongeMatch(m) for m in docDB.search_many('ChallongeMatch', {'player1_id': self['_id']})]:
            m['player1_id'] = None
            m.save()
        for m in [ChallongeMatch(m) for m in docDB.search_many('ChallongeMatch', {'player2_id': self['_id']})]:
            m['player2_id'] = None
            m.save()
        for m in [Media(m) for m in docDB.search_many('Media', {'src_type': 1, 'src': {'$regex': f"^{self['_id']}"}})]:
            m.delete()
        transmit_challonge_delete(self, 'participant')

    def fetch_portrait(self, url, overwrite=False, remove_old=True):
        from elements import Media, User, Setting
        media_user = User.get(Setting.value('challonge_img_user_id'))
        if self['_id'] is None or media_user['_id'] is None:
            return False
        if self['portrait_id'] is not None and not overwrite:
            return True

        portrait = None
        if self['portrait_id'] is None or not remove_old:
            portrait = Media({'src_type': 1, 'user_id': media_user['_id'], 'common': False, 'type': 0, 'desc': f"{self['name']} {self['tournament_id']}"})
            portrait.save()
        else:
            portrait = Media.get(self['portrait_id'])

        if portrait is not None and portrait['_id'] is not None:
            portrait.fetch_and_store(url, filename=self['_id'])
            self['portrait_id'] = portrait['_id']
            self.save(only_on_changes=True)
            return True
        return False
