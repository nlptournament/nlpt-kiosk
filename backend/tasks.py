from invoke import task
import time


@task(name='testdata')
def generate_testdata(c):
    from noapi import docDB
    from elements import Screen, User
    admin_user_id = docDB.search_one('User', {'login': 'admin'})['_id']
    test_user_id = User({'login': 'testuser', 'admin': False, 'pw': 'password'}).save()['created']
    s = Screen({'desc': 'Some TMNF-TAS screen', 'duration': 30})
    s['user_id'] = admin_user_id
    s['template_id'] = docDB.search_one('ScreenTemplate', {'name': 'TrackMania Stats'})['_id']
    s.save()

    s = Screen({'desc': 'Ankündigungen', 'duration': 20, 'repeat': 1})
    s['user_id'] = test_user_id
    s['template_id'] = docDB.search_one('ScreenTemplate', {'name': 'Announcements'})['_id']
    s.save()

    s = Screen({'desc': 'Event Start'})
    s['user_id'] = admin_user_id
    s['template_id'] = docDB.search_one('ScreenTemplate', {'name': 'Countdown'})['_id']
    s['variables'] = {'time': int(time.time()) + 3600}
    s.save()
