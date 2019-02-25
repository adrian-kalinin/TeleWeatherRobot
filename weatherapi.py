import requests
from pytz import timezone
from datetime import datetime


class Weather:
    def __init__(self, weather_token, geo_token):
        """ Initialization """
        self.weather_token = weather_token
        self.geo_token = geo_token
        self.weather_url = f'https://api.darksky.net/forecast/{self.weather_token}/'
        self.geo_url = 'https://maps.googleapis.com/maps/api/geocode/'

    def get_geo(self, adress):
        request = self.geo_url + f'json?address={adress}&key={self.geo_token}&language=ru'
        r = requests.get(request).json()
        results = dict()

        if r['status'] == 'OK':
            adress = r['results'][0]['address_components']

            for item in adress:
                if 'country' in item['types']:
                    results['country'] = item['long_name']
                if 'locality' in item['types'] or 'sublocality'in item['types'] or 'postal_town'in item['types']:
                    results['city'] = item['long_name']

            results.update(r['results'][0]['geometry']['location'])

            return results
        
        return None

    def get_weather(self, name):
        """ Gets current weather """
        geo = self.get_geo(name)
        if geo:
            request = (self.weather_url + f'{str(geo["lat"])},{str(geo["lng"])}'
                       + '?exclude=minutely,daily,alerts,flags&lang=ru&units=si&timezone=Tampa')
            r = requests.get(request).json()

            if r:
                weather = {'country': geo['country'],
                           'city': geo['city'],
                           'time': datetime.now(timezone(r['timezone'])).strftime('%H:%M'),
                           'summary': r['currently']['summary'],
                           'apparentTemperature': r['currently']['apparentTemperature'],
                           'temperature': r['currently']['temperature'],
                           'wind': r['currently']['windSpeed'],
                           'humidity': r['currently']['humidity'],
                           'icon': r['currently']['icon'],
                           '+2': r['hourly']['data'][2]['temperature'],
                           '+4': r['hourly']['data'][4]['temperature'],
                           '+6': r['hourly']['data'][6]['temperature'],
                           '+8': r['hourly']['data'][8]['temperature'],
                           '+10': r['hourly']['data'][10]['temperature'],
                           '+12': r['hourly']['data'][12]['temperature']}

                return weather
            