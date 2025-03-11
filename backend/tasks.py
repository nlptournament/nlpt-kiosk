from invoke import task


@task(name='testdata')
def generate_testdata(c):
    from noapi import docDB
    from elements import Screen
    s = Screen({'desc': 'Some TMNF-TAS screen', 'duration': 30})
    s['user_id'] = docDB.search_one('User', {'login': 'admin'})['_id']
    s['template_id'] = docDB.search_one('ScreenTemplate', {'name': 'TrackMania Stats'})['_id']
    s.save()
