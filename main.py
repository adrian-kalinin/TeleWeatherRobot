from aiohttp import web
import telebot
import ssl
import requests
import time

from utils import *
import config

bot = telebot.TeleBot(config.bot_token)
weather = WeatherAPI(config.darksky_key, config.geocoding_token)
render = Render()


def check_mass(msg):
    if msg.chat.id in config.admins:
        text = msg.text
        caption = msg.caption
        if (text and '/mass' in text and not text.strip() == '/mass') or (caption and '/mass' in caption):
            return True


@bot.message_handler(content_types=['photo', 'text'], func=check_mass)
def handle_mass_mailing(message):
    successful, failed = mass_mailing(message)
    with DBHelper() as db:
        lang = db.get(message.from_user.id, 'lang')
    bot.send_message(message.chat.id, messages['mass'][lang].format(successful, failed), parse_mode='html')


def mass_mailing(message):
    successful, failed = 0, 0
    with DBHelper() as db:
        users = db.get_users()

    for user in users:
        try:
            if message.photo:
                file_id = message.photo[0].file_id
                path = bot.get_file(file_id).file_path
                photo = requests.get(f'https://api.telegram.org/file/bot{config.bot_token}/{path}')

                caption = message.caption.replace('/mass', '').strip()
                caption = None if caption == '' else caption
                bot.send_photo(user, photo.content, caption=caption)

            elif message.text:
                text = message.text.replace('/mass', '').strip()
                if not text: return 0, 0
                bot.send_message(user, text)

            successful += 1
            time.sleep(1 / 30)

        except telebot.apihelper.ApiException:
            with DBHelper() as db:
                db.del_user(user)
            failed += 1

    return successful, failed


@bot.message_handler(commands=['start'])
def handle_start(message):
    with DBHelper() as db:
        db.add_user(message.from_user.id)
        lang = db.get(message.from_user.id, 'lang')

        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        favourite = db.get(message.from_user.id, 'favourite')
        if favourite: user_markup.row(favourite)
        user_markup.row(messages['stat'][lang], messages['settings'][lang])

    bot.send_message(message.chat.id, messages['start'], reply_markup=user_markup)


@bot.message_handler(commands=['help'])
def handle_help(message):
    with DBHelper() as db:
        lang = db.get(message.from_user.id, 'lang')
        bot.send_message(message.chat.id, messages['help'][lang])


@bot.message_handler(commands=['about'])
def handle_about(message):
    with DBHelper() as db:
        lang = db.get(message.from_user.id, 'lang')
        bot.send_message(message.chat.id, messages['about'][lang], parse_mode='html')


@bot.message_handler(func=lambda msg: msg.text in messages['settings'].values())
def handle_settings(message):
    with DBHelper() as db:
        lang = db.get(message.chat.id, 'lang')

        keyboard = telebot.types.InlineKeyboardMarkup()
        callback_button_en = telebot.types.InlineKeyboardButton(text='English 🇬🇧', callback_data='change_lang_en')
        callback_button_ru = telebot.types.InlineKeyboardButton(text='Русский 🇷🇺', callback_data='change_lang_ru')
        keyboard.add(callback_button_en, callback_button_ru)

        bot.send_message(message.chat.id, messages['current_lang'][lang], reply_markup=keyboard)


@bot.message_handler(func=lambda msg: msg.text in messages['stat'].values())
def handle_stat(message):
    with DBHelper() as db:
        lang = db.get(message.from_user.id, 'lang')
        personal_stat = db.get(message.from_user.id, 'stat')
        total_stat = db.get_total_amount_stat()
        users_amount = db.get_amount_of_users()

        text = messages['statistics'][lang].format(total_stat, personal_stat, users_amount)
        bot.send_message(message.chat.id, text, parse_mode='html')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    with DBHelper() as db:
        lang = db.get(message.chat.id, 'lang')
        info = weather.get_weather(message.text, lang=lang)

        if info:
            image = render.make_hourly(info, lang)

            keyboard = telebot.types.InlineKeyboardMarkup()
            callback_button = telebot.types.InlineKeyboardButton(text=messages['make_favourite'][lang],
                                                                 callback_data='add')
            keyboard.add(callback_button)

            bot.send_photo(message.chat.id, image, reply_markup=keyboard, caption=f'{info["city"]}, {info["country"]}')

            stat = db.get(message.from_user.id, 'stat')
            db.set(message.from_user.id, 'stat', stat + 1)
        else:
            bot.send_message(message.chat.id, messages['failed'][lang])


@bot.callback_query_handler(func=lambda call: call.data == 'add')
def callback_inline_add(call):
    with DBHelper() as db:
        lang = db.get(call.from_user.id, 'lang')
        db.set(call.from_user.id, 'favourite', call.message.caption.split(',')[0])

    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row(call.message.caption.split(',')[0])
    user_markup.row(messages['stat'][lang], messages['settings'][lang])

    bot.send_message(call.message.chat.id, messages['added'][lang], reply_markup=user_markup)


@bot.callback_query_handler(func=lambda call: 'change_lang' in call.data)
def callback_inline_change_lang(call):
    with DBHelper() as db:
        lang = call.data.replace('change_lang_', '')

        if not lang == db.get(call.from_user.id, 'lang'):
            db.set(call.from_user.id, 'lang', call.data.replace('change_lang_', ''))

            keyboard = telebot.types.InlineKeyboardMarkup()
            callback_button_en = telebot.types.InlineKeyboardButton(text='English 🇬🇧', callback_data='change_lang_en')
            callback_button_ru = telebot.types.InlineKeyboardButton(text='Русский 🇷🇺', callback_data='change_lang_ru')
            keyboard.add(callback_button_en, callback_button_ru)

            bot.edit_message_text(messages['current_lang'][lang], chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, reply_markup=keyboard)

            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            favourite = db.get(call.from_user.id, 'favourite')
            if favourite: user_markup.row(favourite)
            user_markup.row(messages['stat'][lang], messages['settings'][lang])

            bot.send_message(call.message.chat.id, messages['changed'][lang], reply_markup=user_markup)


async def webhook_handle(request):
    if request.path.replace('/', '') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


def webhook_setup():
    webhook_host = config.host
    webhook_port = config.port
    webhook_listen = '0.0.0.0'  # or probably ip address

    webhook_ssl_cert = 'webhook_cert.pem'
    webhook_ssl_priv = 'webhook_pkey.pem'

    webhook_url_base = f'https://{webhook_host}:{webhook_port}'
    webhook_url_path = f'/{config.bot_token}/'

    app = web.Application()
    app.router.add_post(f'/{config.bot_token}/', webhook_handle)

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url_base + webhook_url_path, certificate=open(webhook_ssl_cert, 'r'))

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(webhook_ssl_cert, webhook_ssl_priv)

    web.run_app(
        app,
        host=webhook_listen,
        port=webhook_port,
        ssl_context=context,
    )


def main():
    webhook_setup()


if __name__ == '__main__':
    main()
