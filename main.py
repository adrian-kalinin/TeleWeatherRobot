from flask import Flask, request, jsonify
import requests
import tgbot
import render
import config
import weatherapi


app = Flask(__name__)
bot = tgbot.Bot(config.tokens['bot'])
weather = weatherapi.Weather(config.tokens['weather'])
maker = render.Render()


tg_commands = {'Help': bot.help,
               'About': bot.about,
               '/help': bot.help,
               '/about': bot.about}

weather_commands = {'Current Weather': [weather.get_current, maker.make_current],
                    '/current': [weather.get_current, maker.make_current]}

queue = dict()


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        data = bot.get_data(r)

        global queue

        if not data == None:

            if data['chat_id'] in queue:
                info = weather_commands[queue[data['chat_id']]][0](data['text'])
                if not info == None: 
                    image = weather_commands[queue[data['chat_id']]][1](info)
                    bot.send_photo(data['chat_id'], image)
                    # bot.send_message(data['chat_id'], info)
                else:
                    bot.send_message(data['chat_id'], 'City was not found.')

                del queue[data['chat_id']]

            elif data['text'] in weather_commands:
                queue[data['chat_id']] = data['text']
                bot.send_message(data['chat_id'], 'Enter name of city.')

            elif data['text'] in tg_commands:
                tg_commands[data['text']](data['chat_id'])

            elif data['text'] == '/start':
                bot.start(data['chat_id'])

            elif data['text'] == '/cat':
                bot.send_cat(data['chat_id'])

            else:
                bot.send_message(data['chat_id'], 'Invalid request, use /help.')
        else:
            pass

        return jsonify(r)
    return '<link rel="icon" href="data:;base64,=">'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
