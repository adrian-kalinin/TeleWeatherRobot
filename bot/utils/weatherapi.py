from datetime import datetime
from pytz import timezone
import requests


class WeatherAPI:
    def __init__(self, weather_token, geo_token):
        self.weather_token = weather_token
        self.geo_token = geo_token
        self.weather_url = f'https://api.darksky.net/forecast/{self.weather_token}/'
        self.geo_url = 'https://maps.googleapis.com/maps/api/geocode/'

    def get_geo(self, address, language):
        request = self.geo_url + f'json?address={address}&key={self.geo_token}&language={language}'
        response = requests.get(request).json()
        results = dict()

        if response['status'] == 'OK':
            address = response['results'][0]['address_components']

            for item in address:
                if 'country' in item['types']:
                    results['country'] = item['long_name']
                if 'locality' in item['types'] or 'sublocality' in item['types'] or 'postal_town' in item['types']:
                    results['city'] = item['long_name']

            results.update(response['results'][0]['geometry']['location'])
            return results

    def get_weather(self, name, language):
        if geo := self.get_geo(name, language):
            lat = str(geo["lat"])
            lng = str(geo["lng"])

            response = requests.get(
                f'{self.weather_url}{lat},{lng}?lang={language}'
                '&exclude=minutely,daily,alerts,flags&&units=si&timezone=Tampa'
            )

            if response.status_code == 200:
                try:
                    json_data = response.json()
                    return {
                        'country': geo['country'],
                        'city': geo['city'],
                        'time': datetime.now(timezone(json_data['timezone'])).strftime('%H:%M'),
                        'summary': json_data['currently']['summary'],
                        'apparentTemperature': json_data['currently']['apparentTemperature'],
                        'temperature': json_data['currently']['temperature'],
                        'wind': json_data['currently']['windSpeed'],
                        'humidity': json_data['currently']['humidity'],
                        'icon': json_data['currently']['icon'],
                        '+2': json_data['hourly']['data'][2]['temperature'],
                        '+4': json_data['hourly']['data'][4]['temperature'],
                        '+6': json_data['hourly']['data'][6]['temperature'],
                        '+8': json_data['hourly']['data'][8]['temperature'],
                        '+10': json_data['hourly']['data'][10]['temperature'],
                        '+12': json_data['hourly']['data'][12]['temperature']
                    }

                except KeyError:
                    pass
