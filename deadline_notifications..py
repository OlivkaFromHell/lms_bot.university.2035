import datetime as dt
import telebot
import schedule
from deadline import deadline_list

from config import token


def send(id, text, reply_markup=keyboard):
    bot.send_message(id, text, reply_markup=reply_markup)


# def check_deadline():
#     for user in user_data:
#         now = dt.datetime.now()
#         deadlines = deadline_list()
#
#         for i in range(0, len(inf), 2):
#             time = f" {inf[i + 1].day}.{inf[i + 1].month} {inf[i + 1].hour}:{inf[i + 1].minute}"
#             ans += inf[i] + time + '\n'
#
#     total_msg = ('Ой-ей, скоро сгорит дедлайн 🔥\n' + dead_msg + 'Я не могу пока проверить, сделал ли ты задание'
#                                                                 ' или нет, разработчикам за это не заплатили\n'
#                                                                 'Поэтому тебе стоит убедиться самому:\n' + 'just do it')
#     send()


bot = telebot.TeleBot(token)

# keyboard
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Мой прогресс', 'Уведомления о дедлайнах')
keyboard.row('Список дедлайнов')

schedule.every().day.at("19:00").do(check_deadline)

while True:
    schedule.run_pending()
