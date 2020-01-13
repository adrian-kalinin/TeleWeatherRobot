# TeleWeatherBot
Telegram bot that shows weather in visual format. Try it out - t.me/TeleWeatherRobot

# User Usage

Just enter a name of any city, district or even street to be more accurate. 

![Example](https://github.com/adreex/TeleWeatherRobot/blob/master/example_for_readmre.png)


# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


Instructions below are specified only for Linux and MacOS.

# Configuration config.py
1. Create a Telegram Bot at **t.me/BotFather** and get the token of your bot, then put it as `bot_token` variable.
2. Go to **darksky.net**, get your API-key for `darksky_token`.
3. And you have to get the last one token `geocoder_token` from **developer.here.com**.
4. Fill your `webhook_host` and `webhook_port` (443, 80, 88 or 8443).

# Deployment
1. Generate quick'n'dirty SSL certificate:
```
openssl genrsa -out webhook_pkey.pem 2048
openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
```
When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply with the same value as your server's ip addres


2. Create virtual environment for Python and install all requirements:
```
virtualenv venv --python=python3
source venv/bin/activate
pip install -r requiremetns.txt
```


3. Just enter `python main.py` in your terminal.
