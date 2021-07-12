import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials


def check_doc_status(user_email):
    # Файл, полученный в Google Developer Console
    CREDENTIALS_FILE = 'creds.json'
    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = '1bl9kvP8VAYhwZbUmmsC5W0EqHoaz9KxLqBK8mlgNsqg'

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    # Пример чтения файла
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='A1:E500',
        majorDimension='ROWS'
    ).execute()

    doc_status = []

    for row in values['values']:
        if row[0] == user_email:
            doc_status = [row[1],
                          row[2],
                          row[3]]
            break

    scan_z, orig_z, scan_diplom = None, None, None
    if doc_status:
        if doc_status[0] == 'есть':
            scan_z = 'получен ✅'
        else:
            scan_z = 'отсутствует ❌'

        if doc_status[1] == 'есть':
            orig_z = 'есть ✅'
        elif doc_status[1] == 'ждем':
            orig_z = 'отправлен 📤'
        elif len(doc_status[1]) > 5:
            orig_z = f'трэк-номер {doc_status[1]}'
        else:
            orig_z = 'отсутствует ❌'

        if doc_status[2] == 'есть':
            scan_diplom = 'получен ✅'
        else:
            scan_diplom = 'отсутствует ❌'

    return [scan_z, orig_z, scan_diplom]


def get_login_learn(user_email):
    # Файл, полученный в Google Developer Console
    CREDENTIALS_FILE = 'creds.json'
    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = '1bl9kvP8VAYhwZbUmmsC5W0EqHoaz9KxLqBK8mlgNsqg'

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    # Пример чтения файла
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='A1:E500',
        majorDimension='ROWS'
    ).execute()

    learn_login = 'no_data'
    try:
        for row in values['values']:
            if row[0] == user_email:
                learn_login = row[4]
                break

    except Exception:
        pass

    return  learn_login


if __name__ == '__main__':
    print(get_login_learn(user_email='gulmira_2181@mail.ru'))
