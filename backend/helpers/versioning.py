

def versions_eq(left, right):
    left_l = list()
    for e in left.strip().split('.'):
        try:
            left_l.append(int(e))
        except Exception:
            left_l.append(e)
    right_l = list()
    for e in right.strip().split('.'):
        try:
            right_l.append(int(e))
        except Exception:
            right_l.append(e)
    while len(left_l) < 4:
        left_l.append(0)
    while len(right_l) < 4:
        right_l.append(0)
    for i in range(4):
        if not isinstance(left_l[i], int) == isinstance(right_l[i], int):  # works even if both are str, the result is True
            return False
        if not left_l[i] == right_l[i]:
            return False
    return True


def versions_lt(left, right):
    left_l = list()
    for e in left.strip().split('.'):
        try:
            left_l.append(int(e))
        except Exception:
            left_l.append(e)
    right_l = list()
    for e in right.strip().split('.'):
        try:
            right_l.append(int(e))
        except Exception:
            right_l.append(e)
    while len(left_l) < 4:
        left_l.append(0)
    while len(right_l) < 4:
        right_l.append(0)
    for i in range(4):
        if isinstance(left_l[i], str) and isinstance(right_l[i], int):
            return True
        if isinstance(left_l[i], int) and isinstance(right_l[i], str):
            return False
        if left_l[i] < right_l[i]:
            return True
        if left_l[i] > right_l[i]:
            return False
    return False


def versions_gt(left, right):
    left_l = list()
    for e in left.strip().split('.'):
        try:
            left_l.append(int(e))
        except Exception:
            left_l.append(e)
    right_l = list()
    for e in right.strip().split('.'):
        try:
            right_l.append(int(e))
        except Exception:
            right_l.append(e)
    while len(left_l) < 4:
        left_l.append(0)
    while len(right_l) < 4:
        right_l.append(0)
    for i in range(4):
        if isinstance(left_l[i], str) and isinstance(right_l[i], int):
            return False
        if isinstance(left_l[i], int) and isinstance(right_l[i], str):
            return True
        if left_l[i] > right_l[i]:
            return True
        if left_l[i] < right_l[i]:
            return False
    return False


def versions_lte(left, right):
    if versions_eq(left, right):
        return True
    if versions_lt(left, right):
        return True
    return False


def versions_gte(left, right):
    if versions_eq(left, right):
        return True
    if versions_gt(left, right):
        return True
    return False


def test_compares():
    print('Success' if versions_eq('1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_eq('1.1.1.alpha1', '1.1.1.alpha1') is True else 'Fail')
    print('Success' if versions_eq('1.1.1', '1.1.1.1') is False else 'Fail')
    print('Success' if versions_lt('1.1.1', '1.1.1.1') is True else 'Fail')
    print('Success' if versions_lt('1.1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_lt('1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_gt('1.1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gt('1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_gt('1.1.1', '1.1.1.1') is False else 'Fail')
    print('Success' if versions_lte('1.1.1', '1.1.1.1') is True else 'Fail')
    print('Success' if versions_lte('1.1.1.1', '1.1.1') is False else 'Fail')
    print('Success' if versions_lte('1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gte('1.1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gte('1.1.1', '1.1.1') is True else 'Fail')
    print('Success' if versions_gte('1.1.1', '1.1.1.1') is False else 'Fail')
    print('Success' if versions_lt('1.2.0.alpha1', '1.2.0') is True else 'Fail')
    print('Success' if versions_lt('1.2.0.alpha1', '1.2.0.beta1') is True else 'Fail')
    print('Success' if versions_lt('1.2.0.alpha1', '1.2.0.alpha2') is True else 'Fail')
    print('Success' if versions_lt('1.2.0.beta1', '1.2.0') is True else 'Fail')
    print('Success' if versions_gt('1.2.0', '1.2.0.alpha1') is True else 'Fail')
    print('Success' if versions_gt('1.2.0.beta1', '1.2.0.alpha1') is True else 'Fail')
    print('Success' if versions_gt('1.2.0.alpha2', '1.2.0.alpha1') is True else 'Fail')
    print('Success' if versions_gt('1.2.0', '1.2.0.beta1') is True else 'Fail')


def run():
    import sys
    from helpers.version import version as current_version
    from elements import Setting
    db_version = Setting.value('version')
    if db_version is None:
        # new install nothing todo
        print('Versioning detected a new install!')
        db_defaults()
        Setting.set('version', current_version)
        return
    if versions_eq(db_version, current_version):
        # nothing todo allready the desired version
        print(f'Versioning detected the DB matches the current version {current_version}')
        return
    if versions_gt(db_version, current_version):
        # error DB is on a newer version that software, better just terminate
        print('Versioning detected the Database is on a newer Version than the software provides! Exiting...')
        sys.exit(0)

    print(f'Versioning performing upgrade from v{db_version} to v{current_version}')

    # Add something like:
    # if versions_lt(db_version, '0.2'):

    db_defaults()

    Setting.set('version', current_version)


def db_defaults():
    from elements import User
    if User.count() == 0:
        u = User({'login': 'admin', 'pw': 'password', 'admin': True})
        u.save()
        print('Versioning detected no user, therefore created a default admin user')
    system_screentemplates()


def system_screentemplates():
    from elements import ScreenTemplate
    # Plain Text
    if ScreenTemplate.count({'name': 'Plain Text'}) == 0:
        vardef = dict({
            'text': {'type': 'text', 'desc': 'The text to display'},
            'text_color': {'type': 'str', 'default': '', 'desc': '(html) color of the text, foreground color is used if not set'},
            'text_size':  {'type': 'int', 'default': 9, 'desc': 'the size of the text, between 1 and 14'}
        })
        ScreenTemplate({
            'key': 'text', 'name': 'Plain Text',
            'desc': 'Just displays some text on the Screen',
            'endless': True, 'duration': None, 'variables_def': vardef}).save()
    # Background Image
    if ScreenTemplate.count({'name': 'Background Image'}) == 0:
        vardef = dict({
            'image': {'type': 'media01', 'desc': 'Media element to be displayed in background, needs to be of type 0 or 1'},
            'text_above': {'type': 'str', 'default': '', 'desc': 'upper line of text'},
            'text_below': {'type': 'str', 'default': '', 'desc': 'lower line of text'},
            'text_color': {'type': 'str', 'default': '', 'desc': '(html) color of the text lines, foreground color is used if not set'},
            'text_space': {'type': 'int', 'default': 0, 'desc': 'space between the two lines of text'}
        })
        ScreenTemplate({
            'key': 'background-image', 'name': 'Background Image',
            'desc': 'Image Media displayed in background, with the option to display text on top',
            'endless': True, 'duration': None, 'variables_def': vardef}).save()
    # Countdown
    if ScreenTemplate.count({'name': 'Countdown'}) == 0:
        vardef = dict({
            'time': {'type': 'ts', 'desc': 'timestamp of the target time, the Countdown ticks towards'},
            'text_above': {'type': 'str', 'default': '', 'desc': 'Text displayed above the Countdown'},
            'text_below': {'type': 'str', 'default': '', 'desc': 'Text displayed below the Countdown'}
        })
        ScreenTemplate({
            'key': 'timer', 'name': 'Countdown',
            'desc': 'Counts down the seconds to a target time',
            'endless': False, 'duration': None, 'variables_def': vardef}).save()
    # Announcements
    if ScreenTemplate.count({'name': 'Announcements'}) == 0:
        ScreenTemplate({
            'key': 'announcements', 'name': 'Announcements',
            'desc': 'displays nlpt.online announcements',
            'endless': True, 'duration': None}).save()
    # Player Counts
    if ScreenTemplate.count({'name': 'Player Counts - Prometheus'}) == 0:
        vardef = dict({
            'src_prom': {'type': 'bool', 'default': True, 'desc': 'Prometheus Source is enabled for this Screen', 'ro': True},
        })
        ScreenTemplate({
            'key': 'player-counts', 'name': 'Player Counts - Prometheus',
            'desc': 'shows the number of players currently active on game-servers',
            'endless': True, 'duration': None, 'variables_def': vardef}).save()
    # Player Counts - Discord
    if ScreenTemplate.count({'name': 'Player Counts - Discord'}) == 0:
        vardef = dict({
            'guild': {'type': 'discordguild', 'default': '', 'desc': 'Only members of this guild are counted'},
            'role': {'type': 'discordrole', 'default': '', 'desc': 'Only members with this role are counted'},
            'src_discord': {'type': 'bool', 'default': True, 'desc': 'Discord Source is enabled for this Screen', 'ro': True},
        })
        ScreenTemplate({
            'key': 'player-counts', 'name': 'Player Counts - Discord',
            'desc': 'shows the number of players playing the same game within Discord guild',
            'endless': True, 'duration': None, 'variables_def': vardef}).save()
    # TrackMania Stats
    if ScreenTemplate.count({'name': 'TrackMania Stats'}) == 0:
        ScreenTemplate({
            'key': 'tas', 'name': 'TrackMania Stats',
            'desc': 'a reduced form of the TrackMania TimeAttackServer wallboard',
            'endless': True, 'duration': None}).save()
    # Video
    if ScreenTemplate.count({'name': 'Video'}) == 0:
        vardef = dict({
            'video': {'type': 'media2', 'desc': 'Media element to be played'}
        })
        ScreenTemplate({
            'key': 'video-player', 'name': 'Video',
            'desc': 'Video is played fullscreen',
            'endless': False, 'duration': None, 'variables_def': vardef}).save()
    # Stream
    if ScreenTemplate.count({'name': 'Stream'}) == 0:
        vardef = dict({
            'stream': {'type': 'media3', 'desc': 'Media element to be played'}
        })
        ScreenTemplate({
            'key': 'stream-player', 'name': 'Stream',
            'desc': 'Stream is played fullscreen',
            'endless': True, 'duration': None, 'variables_def': vardef}).save()
    # Challonge Round Completion
    if ScreenTemplate.count({'name': 'Challonge Round Completion'}) == 0:
        vardef = dict({
            'title': {'type': 'str', 'default': '', 'desc': 'optional title to show on top of Screen, otherqise Tournament name is displayed'},
            'tournament_id': {'type': 'int', 'desc': 'ID of the challonge tournament to display'},
            'signal_completed': {'type': 'bool', 'default': False, 'desc': 'if enabled the completion of a (primary) round signals a finished'}
        })
        ScreenTemplate({
            'key': 'challonge-rc', 'name': 'Challonge Round Completion',
            'desc': 'Shows the pairs and their completion of the current round in a challonge tournament',
            'endless': True, 'duration': None, 'variables_def': vardef}).save()
    # Challonge Parallel Tournaments
    if ScreenTemplate.count({'name': 'Challonge Parallel Tournaments'}) == 0:
        vardef = dict({
            'title': {'type': 'str', 'default': '', 'desc': 'optional title to show on top of Screen'},
            'tournament1_id': {'type': 'int', 'desc': 'ID of one challonge tournament to display'},
            'tournament2_id': {'type': 'int', 'desc': 'ID of other challonge tournament to display'},
            'signal_completed': {'type': 'bool', 'default': False,
                                 'desc': 'if enabled Screen signals finished if the same (latest, primary) rounds on both Tournaments are completed'}
        })
        ScreenTemplate({
            'key': 'challonge-pt', 'name': 'Challonge Parallel Tournaments',
            'desc': 'Shows the pairs and their completion of the current round in two parallel executed Tournaments',
            'endless': True, 'duration': None, 'variables_def': vardef}).save()
