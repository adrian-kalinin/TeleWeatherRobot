import requests


class Weather:
    def __init__(self, token):
        """ Initialization """
        self.token = token
        self.url = 'https://api.openweathermap.org/data/2.5/'

    def get_current(self, name):
        """ Gets current weather """
        request = self.url + f'weather?q={name}&units=metric&appid={self.token}'
        data = requests.get(request).json()

        if data['cod'] == 200:
            current_weather = {'name': data['name'],
                               'temp': data['main']['temp'],
                               'wind': data['wind']['speed'],
                               'humidity': data['main']['humidity'],
                               'id': data['weather'][0]['id']}
            return current_weather
        return None
