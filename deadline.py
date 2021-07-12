import datetime as dt
import requests
import json

from config import moodle_token


def deadline_list(moodle_id):
    r = requests.get(f'https://dl-iamt.spbstu.ru/webservice'
                     f'/rest/server.php?wstoken={moodle_token}&wsfunction='
                     f'get_analyticsbot&moodlewsrestformat=json&userId={moodle_id}')

    ans = json.loads(r.text[:-4])
    dead_courses = []

    for index_c, course in enumerate(ans['courses']):
        if 'quiz' in str(course):
            for index_t, task in enumerate(ans['courses'][index_c]['quiz']):
                name = ans['courses'][index_c]['quiz'][index_t]['name']
                timeclose = ans['courses'][index_c]['quiz'][index_t]['timeclose']
                timeclose = dt.datetime.utcfromtimestamp(int(timeclose))
                dead_courses.append({'name': name, 'timeclose': timeclose})

    list_to_send = []
    # за месяц
    for dead in dead_courses:
        if 0 < (dead['timeclose'] - dt.datetime.now()).days < 28 and dead['timeclose'] != dt.datetime(1970, 1, 1, 0, 0):
            list_to_send.append(dead)

    if list_to_send:
        for row in list_to_send:
            msg = 'Список дедлайнов на месяц:\n\n'
            time = row['timeclose'].strftime("%d.%m %H:%M")
            row_name = row['name']
            msg += f'{row_name} | {time}\n\n'
    else:
        msg = 'На текущий месяц дедлайнов нет'

    return msg


if __name__ == '__main__':
    print(deadline_list(27947))


