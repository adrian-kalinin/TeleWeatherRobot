import sys, os, ids
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO


class Render:
    def __init__(self):
        """ Initialization """
        self.cwd = os.getcwd()
        self.id = ids.id

    def make_current(self, data):
        """ Makes picture about current weather """
        city = data['name']
        temp = data['temp']
        weather = self.id[data['id']]['cond'].split()
        wind = data['wind']

        if temp <= 10 and wind > 1.5:
            feelslike = 'feels like ' + str(round(13.12 + 0.625*int(temp)
            - 11.37*(int(wind)**0.16) + 0.3965*int(temp)*(int(wind)**0.16)))+'°'
        else:
            feelslike = 'feels like ' + str(round(int(temp)))+'°'

        temp = str(round(temp)) + '°'
        wind = str(round(wind)) + ' m/s'

        im = Image.open(self.cwd + '/backgrounds/' + self.id[data['id']]['name']
             + '.png').convert("RGBA")
        ic = Image.open(self.cwd + '/icons/' + self.id[data['id']]['name']
             + '.png')
        wind_ic = Image.open(self.cwd + '/icons/wind.png')
        txt = Image.new('RGBA', im.size, (255,255,255,0))

        font_h = self.cwd + '/fonts/ObjectSans-Heavy.otf'
        font_l = self.cwd + '/fonts/ObjectSans-Regular.otf'

        temp_font = ImageFont.truetype(font=font_h, size=108)
        city_font = ImageFont.truetype(font=font_l, size=32)
        feelslike_font = ImageFont.truetype(font=font_l, size=30)
        weather_font = ImageFont.truetype(font=font_l, size=50)
        wind_font = ImageFont.truetype(font=font_l, size=28)

        im.paste(ic, (74, int(im.size[1]/2-ic.size[1]/2)), ic)
        draw = ImageDraw.Draw(txt)
        tsize = ImageDraw.Draw(txt).textsize
        draw.text((im.width - tsize(city, city_font)[0] - 77, 42), city,
            font=city_font)
        draw.text((im.width - tsize(temp, temp_font)[0] - 77, 86),
            text=temp, font=temp_font)
        draw.text((im.width - tsize(feelslike, feelslike_font)[0] - 77, 185),
            text=feelslike, font=feelslike_font, fill=(255,255,255,168))
        draw.text(((im.width - tsize(wind, wind_font)[0] - 77), 221), text=wind,
            font=wind_font, fill=(255,255,255,168))

        im.paste(wind_ic, (im.width - tsize(wind, wind_font)[0] - 77 - 10
            - wind_ic.width, 218), wind_ic)

        if len(weather) > 1:
            if len(weather[0] + weather[1]) < 12 and len(weather) != 3:
                draw.text((im.width - tsize(weather[0] + ' ' + weather[1],
                          weather_font)[0] - 77, 287), text=weather[0]+ ' '
                          + weather[1], font=weather_font)
            elif len(weather) == 2:
                draw.text((im.width - tsize(weather[0], weather_font)[0] - 77,
                           264), text=weather[0], font=weather_font)
                draw.text((im.width - tsize(weather[1], weather_font)[0] - 77,
                    tsize(weather[1], weather_font)[1] + 264 + 8),
                    text=weather[1], font=weather_font)
            else:
                draw.text((im.width - tsize(weather[0] + ' ' + weather[1],
                           weather_font)[0] - 77, 264), text=weather[0] + ' ' +
                           weather[1], font=weather_font)
                draw.text((im.width - tsize(weather[2], weather_font)[0] - 77,
                           tsize(weather[0], weather_font)[1] + 264 + 8),
                           text=weather[2], font=weather_font)

        else:
            draw.text((im.width - tsize(' '.join(weather), weather_font)[0]
                       - 77, 287), text=' '.join(weather), font=weather_font)

        im = Image.alpha_composite(im, txt)

        bio = BytesIO()
        bio.name = 'image.png'
        im.save(bio, 'png')
        bio.seek(0)

        return bio

# Render().make_current({'name': 'Moscow', 'temp': -11.4, 'wind': 3, 'humidity': 85, 'id': 210})
