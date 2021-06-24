import datetime as dt
import requests
import json


def deadline_list(moodle_id):
    r = requests.get(f'https://moodle.vk-apps.dev/webservice'
                     f'/rest/server.php?wstoken=c6fbe6f2b693c965cd939fcba3526cea&wsfunction='
                     f'get_videolecture&moodlewsrestformat=json&userId={moodle_id}')

    ans = json.loads(r.text[:-4])

    dead_courses = []

    for course in ans['courses']:
        for task in ans['courses'][course]['quiz']:
            name = ans['courses'][course]['quiz'][task]['name']
            timeclose = ans['courses'][course]['quiz'][task]['timeclose']
            timeclose = dt.datetime.utcfromtimestamp(int(timeclose))
            dead_courses.append({'name': name, 'timeclose': timeclose})

    list_to_send = []
    # за месяц
    for dead in dead_courses:
        if 0 < (dead['timeclose'] - dt.datetime.now()).days < 24 and dead['timeclose'] != dt.datetime(1970, 1, 1, 0, 0):
            list_to_send.append(dead)

    for row in list_to_send:
        msg = 'Список дедлайнов на месяц:\n'
        time = row['timeclose'].strftime("%d.%m %H:%M")
        msg += row['name'] + ' | ' + time + '\n'
    else:
        msg = 'На текущий месяц дедлайнов нет'

    return msg


