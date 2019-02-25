import telebot
import cherrypy
import pickle
import json
import render
import config
import weatherapi
import constants


WEBHOOK_HOST = '159.65.194.171'
WEBHOOK_PORT = 80
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = f'https://{WEBHOOK_HOST}:{WEBHOOK_PORT}'
WEBHOOK_URL_PATH = f'/{config.tokens["bot"]}/'


bot = telebot.TeleBot(config.tokens['bot'])
weather = weatherapi.Weather(config.tokens['weather'], config.tokens['geocoding'])

admins = (291702642, 112903034)
stat = dict()
users = set()


def load_data():
    global stat, users
    try:
        with open('stat.json', 'r', encoding='utf-8') as file:
            stat = json.load(file)
        with open('users.bin', 'rb') as file:
            users = pickle.load(file)
    except:
        pass


@bot.message_handler(commands=['users'])
def handle_start(message):
    text = ''
    if message.chat.id in admins:
        global stat, users

        for user in users:
            text += str(user) + ''
        bot.send_message(message.chat.id, text)

    else:
        bot.send_message(message.chat.id, 'Неккоректный ввод.')


@bot.message_handler(commands=['stat'])
def handle_start(message):
    if message.chat.id in admins:
        global stat, users

        text = (f'{len(users)} пользователей.\n'
                f'{stat["pics"]} картинок с погодой.\n')
        bot.send_message(message.chat.id, text)

    else:
        bot.send_message(message.chat.id, 'Неккоректный ввод.')


@bot.message_handler(commands=['save'])
def handle_start(message):
    global stat, users, admins
    if message.chat.id in admins:
        with open('stat.json', 'w', encoding='utf-8') as file:
            json.dump(stat, file)
        with open('users.bin', 'wb') as file:
            pickle.dump(users, file)
        text = 'Данные успешно сохранены.'
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, constants.start)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, constants.help)


@bot.message_handler(commands=['about'])
def handle_about(message):
    bot.send_message(message.chat.id, constants.about)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    info = weather.get_weather(message.text)
    if info:
        image = render.make_hourly(info)

        keyboard = telebot.types.InlineKeyboardMarkup()
        callback_button = telebot.types.InlineKeyboardButton(text="Сделать избранным", callback_data=1)
        keyboard.add(callback_button)

        bot.send_photo(message.chat.id, image, reply_markup=keyboard, caption=f'{info["city"]}, {info["country"]}')

        global stat
        stat['pics'] += 1
    else:
        bot.send_message(message.chat.id, 'Неккоректный ввод.')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message and call.data:
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row(call.message.caption.split(',')[0])

        bot.send_message(call.message.chat.id, (f'Город *{call.message.caption.split(",")[0]}* добавлен в избранное. '   
                                                'Теперь вы можете просто нажать на кнопку внизу.'),
                         parse_mode='MARKDOWN', reply_markup=user_markup)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':

            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")

            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])

            return ''
        else:
            raise cherrypy.HTTPError(403)


def main():
    load_data()
    bot.remove_webhook()

    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })

    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})


if __name__ == '__main__':
    main()
