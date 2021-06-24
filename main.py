import datetime as dt
import sqlite3
import telebot
import requests
from json import loads

from deadline import deadline_list  # file with list of deadlines
from scores_stat import my_progress  # return web-page with user progress
from config import token

bot = telebot.TeleBot(token)

deadline = dt.datetime(2021, 6, 21)

# keyboard
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Мой прогресс', 'Уведомления о дедлайнах')
keyboard.row('Список дедлайнов')

# notification keyboard
keyboard_deadline = telebot.types.ReplyKeyboardMarkup(True)
keyboard_deadline.row('Отключить уведомления', 'Включить уведомления')


def send(id, text, reply_markup=''):
    'send message to user from bot'
    bot.send_message(id, text, reply_markup=reply_markup)


class User:
    def __init__(self, mail):
        self.mail = mail
        self.notification = True


@bot.message_handler(commands=['start'])
def answer(message):
    msg = bot.send_message(message.chat.id, 'Привет! 👋\nЯ - твой виртуальный помощник на курсе SAPtest.\n'
                                            'Чтобы продолжить работу, необходимо авторизироваться.\n'
                                            'Введи свою электронную почту, с которой ты проходишь данный курс\n'
                                            '⬇')
    bot.register_next_step_handler(msg, process_reg)


def process_reg(message):
    try:

        telegram_id = message.from_user.id
        req = requests.get(f"https://moodle.vk-apps.dev/webservice/rest/server.php?"
                           f"wstoken=c6fbe6f2b693c965cd939fcba3526cea&wsfunction=core_user_get_users"
                           f"&moodlewsrestformat=json&criteria[1][key]=email&criteria[1][value]={message.text}")
        response = loads(req.text)

        if response['users'][0]['email'] == message.text:
            try:
                # connect with sqlite db
                conn = sqlite3.connect("data/user_database.db")
                cursor = conn.cursor()
                sql = "INSERT INTO user_db VALUES (?,?,?,?)"
                val = [(telegram_id, response['users'][0]['id'], response['users'][0]['fullname'],
                        response['users'][0]['email'])]
                cursor.executemany(sql, val)
                conn.commit()


            except sqlite3.IntegrityError:
                pass
                # bot.send_message(message.chat.id, 'Упс.. Кто-то уже зарегистрирован в боте с данным email')
            bot.send_message(message.chat.id, 'Супер, мы определили, кто ты!\n\n'
                                              'Вот несколько моих функций:\n'
                                              'Мой прогресс – покажу твои оценки и комментарии преподавателей\n'
                                              'Список дедлайнов – выведу все горящие дедлайны курса и буду бережно напоминать\n'
                                              'И если вдруг забыл команды – пиши /help\n\n'
                                              'С чего начнем?', reply_markup=keyboard)

        else:
            msg = bot.reply_to(message, 'Что-то я не нашел тебя в базе...\n\n'
                                        'Проверь, с какой почти ты записывался на курс, и попробуй еще раз\n\n'
                                        'Введи электронную почту, с которой ты проходишь данный курс\n\n'
                                        '⬇')
    except Exception as e:
        bot.register_next_step_handler(msg, process_reg)


@bot.message_handler(commands=['help'])
def answer(message):
    help_msg = ('Сообщение при вводе /help:\n\n'
                'У тебя возник вопрос? Мы постараемся на него ответить\n\n'
                'Здесь перечислены краткие возможности бота:\n\n'
                '*Мой прогресс* – с помощью этой команды ты можешь'
                'посмотреть свои текущие оценки по сданным работам, а также средний балл\n\n'
                '*Список дедлайнов* – нажав на эту кнопку, ты получишь список всех дедлайнов, которые есть на курсе.\n\n'
                '*Уведомления о дедлайнах* – здесь ты можешь включить или выключить уведомления о дедлайнах. '
                'Если включишь, за сутки до истечения срока сдачи тебе будет приходить уведомление. '
                'Также по понедельникам будет приходить недельный дайджест – какие тесты и задания надо сдать на этой неделе.\n\n'
                'Если возникли какие-то трудности или вылезли баги, пиши разработчику: @itsdaniilts')
    bot.send_message(message.chat.id, help_msg, parse_mode='Markdown')


chat_id_notifications = {}
user_data = {}

@bot.message_handler(content_types=['text'])
def main(message):
    id = message.chat.id
    msg = message.text

    if msg == 'Мой прогресс':
        url = my_progress('alimov.rn@edu.spbstu.ru')
        text = f'[Твой прогресс]({url})'
        send(id, 'Для твоего удобства я визуализировал информацию.\n\n'
                 'Переходи по ссылке и изучай свой прогресс:')
        bot.send_message(id, text, parse_mode='MarkdownV2')

    elif msg == 'Список дедлайнов':
        conn = sqlite3.connect("data/user_database.db")
        cursor = conn.cursor()
        sql = f"SELECT moodle_id FROM user_db WHERE telegram_id = {id}"
        cursor.execute(sql)

        send(id, deadline_list(moodle_id=cursor.fetchone()[0]))
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
    else:
        bot.send_message(id, 'Неправильная команда', reply_markup=keyboard)


bot.polling(none_stop=True)
