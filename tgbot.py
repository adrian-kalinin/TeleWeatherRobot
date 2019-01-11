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
                    'text': r['message']['text'],
                    'name': r['message']['chat']['first_name'],
                    'username': r['message']['chat']['username']}
            return data
        else: 
            return None

    def send_keyboard(self, chat_id):
        """ Makes virtual telegram keyboard """
        url = self.url + 'sendMessage'
        buttons = [['Current Weather'], ['Help', 'About']]
        keyboard = {'keyboard': buttons, 'resize_keyboard': True}
        answer = {'chat_id': chat_id, 'text': '', 'reply_markup': keyboard}
        r = requests.post(url, json=answer)

    def send_message(self, chat_id, text):
        """ Sends message """
        url = self.url + 'sendMessage'
        answer = {'chat_id': chat_id, 'text': text}
        r = requests.post(url, json=answer)

    def send_photo(self, chat_id, im):
        """ Sends image """
        url = self.url + 'sendPhoto'
        files = {'photo': im}
        data = {'chat_id' : chat_id}
        r = requests.post(url, files=files, data=data)

    def help(self, chat_id):
        """ Sends help message """
        text = ('Here is small tutorial how to use this bot.\n'
                '1. Choose and press mode like "Current Weather" or any other.\n'
                '2. Enter name of desired city.\n'
                '3. Get your weather and enjoy.')
        self.send_message(chat_id, text)

    def about(self, chat_id):
        """ Sends about message """
        text = ('This bot has been made by two young and perspective guys from Russia. '
                'We used Python with module requests to work with telegram api, module pillow to make pictures and no more.\n'
                'Developers:\n'
                '@a1f20 - backend programmer.\n'
                '@cantstopwontstop - UI/UX developer.\n')
        self.send_message(chat_id, text)

    def start(self, chat_id):
        """ Sends start message and makes virtual keyboard """
        text = ('Hello! Thanks for using our bot.\n'
                'To see more information read /help and /about.')
        url = self.url + 'sendMessage'
        buttons = [['Current Weather'], ['Help', 'About']]
        keyboard = {'keyboard': buttons, 'resize_keyboard': True}
        answer = {'chat_id': chat_id, 'text': text, 'reply_markup': keyboard}
        r = requests.post(url, json=answer)

    def send_cat(self, chat_id):
        """ Sends cat :D """
        url = self.url + f'sendPhoto?chat_id={chat_id}&photo=http://drobs.ru/opyat/52/kotik_1600x1200.jpg'
        r = requests.get(url)
