import datetime as dt
import telebot

from deadline import deadline_list
from scores_stat import my_progress
from config import token

students = ['alimov.rn@edu.spbstu.ru', 'tregubenko.vyu@edu.spbstu.ru', 'yakushkina.na@edu.spbstu.ru']

bot = telebot.TeleBot(token)

deadline = dt.datetime(2021, 6, 21)

# keyboard
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Мой прогресс', 'Уведомления о дедлайнах')
keyboard.row('Список дедлайнов')

keyboard_deadline = telebot.types.ReplyKeyboardMarkup(True)
keyboard_deadline.row('Отключить уведомления', 'Включить уведомления')


def send(id, text, reply_markup=keyboard):
    bot.send_message(id, text, reply_markup=reply_markup)


def send_without_keyboard(id, text):
    bot.send_message(id, text, reply_markup='')


class User:
    def __init__(self, mail):
        self.mail = mail
        self.notification = True


@bot.message_handler(commands=['start', 'help'])
def answer(message):
    msg = bot.send_message(message.chat.id, 'Привет! 👋\nЯ - твой виртуальный помощник на курсе SAPtest.\n'
                                            'Чтобы продолжить работу, необходимо авторизироваться.\n'
                                            'Введи свою электронную почту, с которой ты проходишь данный курс\n'
                                            '⬇')
    bot.register_next_step_handler(msg, process_reg)


def process_reg(message):
    try:
        if message.text in students:
            user_id = message.from_user.id
            user_data[user_id] = User(message.text)

            bot.send_message(message.chat.id, 'Супер, мы определили, кто ты!\n\n'
                                          'Вот несколько моих функций:\n'
                                          'Мой прогресс – покажу твои оценки и комментарии преподавателей\n'
                                          'Список дедлайнов – выведу все горящие дедлайны курса и буду бережно напоминать\n'
                                          'И если вдруг забыл команды – пиши /help\n\n'
                                          'С чего начнем?')
        else:
            r = 1/0
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Что-то я не нашел тебя в базе...\n\n'
                              'Проверь, с какой почти ты записывался на курс, и попробуй еще раз\n\n'
                              'Введи электронную почту, с которой ты проходишь данный курс\n\n'
                              '⬇')



chat_id_notifications = {}

user_data = {}


@bot.message_handler(content_types=['text'])
def main(message):

    id = message.chat.id
    msg = message.text

    if msg in students:
        send(id, 'Супер, мы определили, кто ты!\n\n'
                 'Вот несколько моих функций:\n'
                 'Мой прогресс – покажу твои оценки и комментарии преподавателей\n'
                 'Список дедлайнов – выведу все горящие дедлайны курса и буду бережно напоминать\n'
                 'И если вдруг забыл команды – пиши /help\n\n'
                 'С чего начнем?')
        chat_id_notifications.update({id: True})

    elif msg == 'Сколько дней до дедлайна?':
        now = dt.datetime.now()
        days_left = deadline - now
        ans = f"До сдачи проекта осталось {days_left.days} дней"
        send(id, ans)
    elif msg == 'Мой прогресс':
        url = my_progress('alimov.rn@edu.spbstu.ru')
        text = f'[Твой прогресс]({url})'
        send(id, 'Для твоего удобства я визуализировал информацию.\n\n'
                 'Переходи по ссылке и изучай свой прогресс:')
        bot.send_message(id, text, parse_mode='MarkdownV2')

    elif '@' in msg:
        send_without_keyboard(id, 'Что-то я не нашел тебя в базе...\n\n'
                                  'Проверь, с какой почти ты записывался на курс, и попробуй еще раз\n\n'
                                  'Введи электронную почту, с которой ты проходишь данный курс\n\n'
                                  '⬇')

    elif msg == 'Список дедлайнов':
        send(id, deadline_list())
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
