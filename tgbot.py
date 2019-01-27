import requests


class Bot:
    def __init__(self, token):
        """ Initialization """
        self.token = token
        self.url = 'https://api.telegram.org/bot' + self.token + '/'

    def get_data(self, r):
        """ Takes useful data from update """     
        if 'text' in r['message']:
            data = {'chat_id': r['message']['chat']['id'],
                    'text': r['message']['text']}
            return data
        else: 
            return None

    def send_message(self, chat_id, text):
        """ Sends message """
        url = self.url + 'sendMessage'
        answer = {'chat_id': chat_id, 'text': text, 'offset': 'UTF-8'}
        r = requests.post(url, json=answer)

    def send_photo(self, chat_id, im):
        """ Sends image """
        url = self.url + 'sendPhoto'
        files = {'photo': im}
        data = {'chat_id' : chat_id}
        r = requests.post(url, files=files, data=data)

    def help(self, chat_id):
        """ Sends help message """
        text = ('Просто введите название любого города, района, улицы или даже название торгового центра и получите погоду этого места в визуальном формате.')
        self.send_message(chat_id, text)

    def about(self, chat_id):
        """ Sends about message """
        text = ('Разработчики:\n'
                '@a1f20 - бэкэнд программист.\n'
                '@dead_insider - фронтэнд разработчик.\n')
        self.send_message(chat_id, text)

    def start(self, chat_id):
        """ Sends start message and makes virtual keyboard """
        text = ('Спасибо за использование нашего бота, сначала рекомендуем прочитать /help и /about.')
        self.send_message(chat_id, text)

    def send_cat(self, chat_id):
        """ Sends cat :D """
        url = self.url + f'sendPhoto?chat_id={chat_id}&photo=http://drobs.ru/opyat/52/kotik_1600x1200.jpg'
        r = requests.get(url)
