from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

import config
from .constants import messages, buttons
from .utils import DataBase, WeatherAPI, Render


def handle_start(bot, message):
    with DataBase() as db:
        db.add_user(message.from_user.id)
        language = db.get_language(message.from_user.id)

        user_markup = ReplyKeyboardMarkup(True, False)
        if favourite := db.get_favourite(message.from_user.id):
            user_markup.row(favourite)
        user_markup.row(buttons['statistics'][language], buttons['settings'][language])

    bot.send_message(message.chat.id, messages['start'], reply_markup=user_markup)


def handle_help(bot, message):
    with DataBase() as db:
        language = db.get_language(message.from_user.id)
        bot.send_message(message.chat.id, messages['help'][language])


def handle_settings(bot, message):
    with DataBase() as db:
        language = db.get_language(message.chat.id)

        keyboard = InlineKeyboardMarkup()
        callback_button_en = InlineKeyboardButton(text='English 🇬🇧', callback_data='change_lang_en')
        callback_button_ru = InlineKeyboardButton(text='Русский 🇷🇺', callback_data='change_lang_ru')
        keyboard.add(callback_button_en, callback_button_ru)

        bot.send_message(message.chat.id, messages['current_lang'][language], reply_markup=keyboard)


def handle_statistics(bot, message):
    with DataBase() as db:
        language = db.get_language(message.from_user.id)
        personal_stat = db.get_requests(message.from_user.id)
        requests_amount = db.get_requests_amount()
        users_amount = db.get_users_amount()

        text = messages['statistics'][language].format(requests_amount, personal_stat, users_amount)
        bot.send_message(message.chat.id, text, parse_mode='html')


def handle_text(bot, message):
    with DataBase() as db:
        language = db.get_language(message.chat.id)

        weather = WeatherAPI(config.darksky_token, config.geocoder_token)
        info = weather.get_weather(message.text, language=language)

        if info:
            image = Render().make_hourly(info, language)

            keyboard = InlineKeyboardMarkup()
            callback_button = InlineKeyboardButton(text=messages['make_favourite'][language], callback_data='add')
            keyboard.add(callback_button)

            bot.send_photo(message.chat.id, image, reply_markup=keyboard, caption=f'{info["city"]}, {info["country"]}')

            requests = db.get_requests(message.from_user.id)
            db.set_requests(message.from_user.id, requests + 1)
        else:
            bot.send_message(message.chat.id, messages['failed'][language])


def callback_inline_add(bot, call):
    with DataBase() as db:
        language = db.get_language(call.from_user.id)
        db.set_favourite(call.from_user.id, call.message.caption.split(',')[0])

    user_markup = ReplyKeyboardMarkup(True, False)
    user_markup.row(call.message.caption.split(',')[0])
    user_markup.row(buttons['statistics'][language], buttons['settings'][language])

    bot.send_message(call.message.chat.id, messages['added'][language], reply_markup=user_markup)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup())


def callback_inline_change_lang(bot, call):
    with DataBase() as db:
        language = call.data.replace('change_lang_', '')

        if not language == db.get_language(call.from_user.id):
            db.set_language(call.from_user.id, call.data.replace('change_lang_', ''))

        user_markup = ReplyKeyboardMarkup(True, False)
        if favourite := db.get_favourite(call.from_user.id):
            user_markup.row(favourite)
        user_markup.row(buttons['statistics'][language], buttons['settings'][language])

        bot.send_message(call.message.chat.id, messages['changed'][language], reply_markup=user_markup)
        bot.delete_message(call.message.chat.id, call.message.message_id)
