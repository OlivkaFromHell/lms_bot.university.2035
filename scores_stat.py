import pandas as pd
import requests
from json import loads


def my_progress(user_mail):
    url = f"https://study.vk-apps.dev/api/fetchData"

    file = pd.read_excel('data/grade_history.xlsx')

    filter_1 = file['Источник'] == 'mod/quiz'
    filter_2 = file['Адрес электронной почты'] == user_mail

    user_info = file.loc[filter_1 & filter_2]
    user_info = user_info[['Дата и время', 'Элемент оценивания', 'Исправленная оценка']].rename(
        columns={'Исправленная оценка': 'Оценка'})

    info_json = user_info.to_json()
    res = requests.post(f"{url}?data={info_json}")
    response = loads(res.text)

    return response['url']
