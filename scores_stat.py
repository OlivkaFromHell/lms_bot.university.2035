import requests
from json import loads, dumps

from config import moodle_token


def my_progress(moodle_id):
    url = "https://study.vk-apps.dev/api/fetchData"
    r = requests.get('https://dl-iamt.spbstu.ru/webservice/rest/server.php'
        f'?wstoken={moodle_token}&wsfunction='
        f'get_analyticsbot&moodlewsrestformat=json&userId={moodle_id}')

    text = r.text[:-4].replace('\n', ' ').replace(r'<p>', '').replace('<\/p>', ' ')#.replace('\"', '\'')
    scores = loads(text)


    user_info = {}
    count = 0
    for course in scores['courses']:
        if 'quiz' in str(course):
            for quiz in course['quiz']:
                if 'id' in str(quiz) and (quiz['grade'] != 0 and quiz['grade'] != 'null' and quiz['grade']):
                    if 'comment' in str(quiz) and quiz['comment']:
                        user_info.update({count: {'Элемент оценивания': quiz['name'],
                                                  'Оценка': quiz['grade'], 'Комментарий': quiz['comment']}})
                    else:
                        user_info.update({count: {'Элемент оценивания': quiz['name'], 'Оценка': quiz['grade']}})
                    count += 1

    info_json = dumps(user_info)

    res = requests.post(url, data={'data': info_json})
    response = loads(res.text)

    return response['url']


if __name__ == '__main__':
    print(my_progress(27952))
