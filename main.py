from flask import Flask, request, jsonify
import requests
import pickle
import json
import tgbot
import render
import config
import weatherapi


app = Flask(__name__)
bot = tgbot.Bot(config.tokens['bot'])
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

def save_data(chat_id):
    global stat, users, admins
    if chat_id in admins:
        with open('stat.json', 'w', encoding='utf-8') as file:
            json.dump(stat, file)
        with open('users.bin', 'wb') as file:
            pickle.dump(users, file)
        text = 'Данные успешно сохранены.'
        bot.send_message(chat_id, text)

def get_stat(chat_id):
    global stat, users
    if chat_id in admins:
        text = (f'{len(users)} пользователей.\n'
                f'{stat["messages"]} сообщений.\n'
                f'{stat["pics"]} картинок с погодой.\n'
                f'{stat["cats"]} котиков.\n')
        bot.send_message(chat_id, text)

def get_users(chat_id):
    global stat, users
    text = ''
    if chat_id in admins:
        for user in users:
            text  += str(user) + '\n'
        bot.send_message(chat_id, text)


tg_commands = {'/help': bot.help,
               '/about': bot.about,
               '/start': bot.start,
               '/cat': bot.send_cat}

admin_commands = {'/stat': get_stat,
                  '/users': get_users,
                  '/save': save_data}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        data = bot.get_data(r)

        global users, stat, tg_commands, admin_commands, admins

        if not data == None:
            if not data['chat_id'] in users: users.add(data['chat_id']) 

            elif data['text'] in tg_commands:
                tg_commands[data['text']](data['chat_id'])

            elif data['text'] in admin_commands:
                admin_commands[data['text']](data['chat_id'])

            else:
                info = weather.get_weather(data['text'])
                if not info == None:
                    image = render.make_hourly(info)
                    bot.send_photo(data['chat_id'], image)

                
                else:
                    text = 'Некорректный ввод.'
                    bot.send_message(data['chat_id'], text)
            
            stat['messages'] += 1

        else:
            pass

        return jsonify(r)
    return '<link rel="icon" href="data:;base64,=">'


if __name__ == '__main__':
    load_data()
    app.run(host='0.0.0.0', port=5000)
