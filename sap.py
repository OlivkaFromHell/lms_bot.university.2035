import sqlite3
import logging
import requests
from json import loads
import telebot

from deadline import deadline_list  # file with list of deadlines
from scores_stat import my_progress  # return web-page with user progress
from google_doc_status import check_doc_status, get_login_learn  # check doc status
from config import token, moodle_token

bot = telebot.TeleBot(token)

# keyboard
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Мой прогресс', 'Уведомления о дедлайнах')
keyboard.row('Статус документов', 'Список дедлайнов')

# notification keyboard
keyboard_deadline = telebot.types.ReplyKeyboardMarkup(True)
keyboard_deadline.row('Отключить уведомления', 'Включить уведомления')


def send(id, text, parse_mode='', reply_markup=''):
    """send message to user from bot"""
    bot.send_message(id, text, parse_mode=parse_mode, reply_markup=reply_markup)


def reauth(message):
    bot.reply_to(message, 'Что-то я не нашел тебя в базе...\n\n'
                          'Проверь, с какой почти ты записывался на курс, и попробуй еще раз\n\n'
                          'Введи электронную почту, с которой ты проходишь данный курс\n\n'
                          '⬇')
    bot.register_next_step_handler(message, process_reg)


logging.basicConfig(format="%(asctime)s %(message)s",
                    filename='sap.log')


@bot.message_handler(commands=['start'])
def auth(message):
    msg = bot.send_message(message.chat.id, 'Привет! 👋\nЯ - твой виртуальный помощник на курсе SAPtest.\n'
                                            'Чтобы продолжить работу, необходимо авторизироваться.\n'
                                            'Введи свою электронную почту, с которой ты проходишь данный курс\n'
                                            '⬇')

    bot.register_next_step_handler(msg, process_reg)


def process_reg(message):
    auth_passed = False
    learn_login = 'no_data'
    telegram_id = message.from_user.id
    response = []

    try:
        req = requests.get(f"https://dl-iamt.spbstu.ru/webservice/rest/server.php?"
                           f"wstoken={moodle_token}&moodlewsrestformat=json&wsfunction=core_user_get_users_by_field"
                           f"&field=email&values[]={message.text}")
        response = loads(req.text)
        assert response[0]

    except Exception as err:
        err_msg = f"User with email |{message.text}| while auth got error: {err}"
        logging.error(err_msg)

    if response:

        try:
            learn_login = get_login_learn(message.text)
        except Exception as err:
            err_msg = f"User with email |{message.text}| while using get_login_learn got error: {err}"
            logging.error(err_msg)

        try:
            # connect with sqlite db
            conn = sqlite3.connect("data/user_database.db")
            cursor = conn.cursor()
            sql = "REPLACE INTO user_db VALUES (?,?,?,?,?,?)"
            val = [(telegram_id, response[0]['id'], response[0]['fullname'],
                    response[0]['email'], message.chat.username, learn_login)]
            cursor.executemany(sql, val)
            conn.commit()
            auth_passed = True

        except Exception as err:
            err_msg = f"User |{message.chat.username}| email |{message.text}| while auth_sql got error: {err}"
            logging.error(err_msg)
        finally:
            cursor.close()
            conn.close()

    if auth_passed:
        msg = 'Супер, мы определили, кто ты!\n\n'
        if learn_login != 'no_data':
            msg += f'Твой логин в S/4: {learn_login}\n\n'
        msg += (
            'Вот несколько моих функций:\n'
            '*Мой прогресс* – покажу твои оценки и комментарии преподавателей\n'
            '*Список дедлайнов* – выведу все'
            'горящие дедлайны курса и буду бережно напоминать\n'
            '*Статус документов* – узнаем, все ли твои документы «на месте»\n'
            'И если вдруг забыл команды или возникли трудности – пиши */help*\n\n'
            'С чего начнем?'
        )

        bot.send_message(message.chat.id, msg, parse_mode='Markdown', reply_markup=keyboard)

    elif message.text != '/start':
        reauth(message)


@bot.message_handler(commands=['help'])
def answer(message):
    help_msg = ('Сообщение при вводе /help:\n\n'
                'У тебя возник вопрос? Мы постараемся на него ответить\n\n'
                'Здесь перечислены краткие возможности бота:\n\n'
                '*Мой прогресс* – с помощью этой команды ты можешь '
                'посмотреть свои текущие оценки по сданным работам, а также средний балл\n\n'
                '*Список дедлайнов* – нажав на эту кнопку, '
                'ты получишь список всех дедлайнов, которые есть на курсе.\n\n'
                '*Уведомления о дедлайнах* – здесь ты можешь включить или выключить уведомления о дедлайнах. '
                'Если включишь, за сутки до истечения срока сдачи тебе будет приходить уведомление. '
                'Также по понедельникам будет приходить недельный '
                'дайджест – какие тесты и задания надо сдать на этой неделе.\n\n'
                '*Статус документов* - здесь можно посмотреть, '
                'в каком статусе находятся отправленные для курса документы\n\n'
                'Если возникли какие-то трудности или вылезли баги, пиши разработчику: *@itsdaniilts*')
    bot.send_message(message.chat.id, help_msg, parse_mode='Markdown')


chat_id_notifications = {}
user_data = {}


@bot.message_handler(content_types=['text'])
def main(message):
    id = message.chat.id
    msg = message.text

    if msg == 'Мой прогресс':
        try:
            conn = sqlite3.connect("data/user_database.db")
            cursor = conn.cursor()
            sql = f"SELECT moodle_id FROM user_db WHERE telegram_id = {id}"
            cursor.execute(sql)

            moodle_id = cursor.fetchone()[0]
            url = my_progress(moodle_id)
            text = f'[Твой прогресс]({url})'
            send(id, 'Для твоего удобства я визуализировал информацию.\n\n'
                     'Переходи по ссылке и изучай свой прогресс:')

            bot.send_message(id, text, parse_mode='MarkdownV2')
            cursor.close()
            conn.close()
        except Exception as err:
            err_msg = f"User |{message.chat.username}| email |{message.text}| while 'Мой прогресс' got error: {err}"
            logging.error(err_msg)

    elif msg == 'Список дедлайнов':
        try:
            conn = sqlite3.connect("data/user_database.db")
            cursor = conn.cursor()
            sql = f"SELECT moodle_id FROM user_db WHERE telegram_id = {id}"
            cursor.execute(sql)
            send(id, deadline_list(moodle_id=cursor.fetchone()[0]))

            cursor.close()
            conn.close()
        except Exception as err:
            err_msg = f"User |{message.chat.username}| email |{message.text}| while 'Список дедлайнов' got error: {err}"
            logging.error(err_msg)

    elif msg == 'Уведомления о дедлайнах':
        send(id, 'Ты можешь включить уведомления о дедлайнах на курсе.'
                 'Теперь ты с меньшей вероятностью пропустишь тест или практическое задание. Наверно...\n\n'
                 'Выбери нужную функцию\n\n⬇', reply_markup=keyboard_deadline)

    elif msg == 'Включить уведомления':
        chat_id_notifications[id] = True
        text_on = ('Уведомления о дедлайнах *включены*\n\n'
                   '*За сутки* до того, как дедлайн сгорит, '
                   'карета превратится в тыкву, и ты воскликнешь “шеф, все пропало”, я напомню тебе о нем \n\n'
                   'А *по понедельникам* я буду кидать тебе дайджест текущих задач на курсе\n\n'
                   'Не пропусти!')
        bot.send_message(id, text_on, parse_mode='Markdown', reply_markup=keyboard)

    elif msg == 'Отключить уведомления':
        chat_id_notifications[id] = False
        text_off = ('Уведомления о дедлайнах *отключены*\n\n'
                    'Будь внимателен, теперь за ними нужно следить самому!')
        bot.send_message(id, text_off, parse_mode='Markdown', reply_markup=keyboard)

    elif msg == 'Статус документов':
        try:
            conn = sqlite3.connect("data/user_database.db")
            cursor = conn.cursor()
            sql = f"SELECT email FROM user_db WHERE telegram_id = {id}"
            cursor.execute(sql)
            doc_status = check_doc_status(cursor.fetchone()[0])
            if None not in doc_status:
                bot.send_message(id,'Здесь отображается статус отправленных документов\n\n'
                                            f'*Скан заявления*: {doc_status[0]}\n'
                                            f'*Оригинал заявления*: {doc_status[1]}\n'
                                            f'*Скан диплома*: {doc_status[2]}\n',
                                            parse_mode='Markdown', reply_markup=keyboard)
                cursor.close()
                conn.close()
            else:
                send(id, 'К сожалению, я не нашел тебя в базе данных с документами')
        except Exception as err:
            err_msg = f"User |{message.chat.username}| email |{message.text}| while 'Статус доков' got error: {err}"
            logging.error(err_msg)

    else:
        bot.send_message(id, 'Неправильная команда', reply_markup=keyboard)


bot.polling(none_stop=True)
