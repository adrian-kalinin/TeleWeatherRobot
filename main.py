from threading import Thread
from telebot import TeleBot
from telebot.types import Update
from aiohttp import web
import ssl

from bot import handlers
from bot import buttons
import config

bot = TeleBot(config.bot_token)


@bot.message_handler(commands=['start'])
def handle_start(message):
    Thread(target=handlers.handle_start, args=(bot, message)).start()


@bot.message_handler(commands=['help'])
def handle_help(message):
    Thread(target=handlers.handle_help, args=(bot, message)).start()


@bot.message_handler(func=lambda msg: msg.text in buttons['settings'].values())
def handle_settings(message):
    Thread(target=handlers.handle_settings, args=(bot, message)).start()


@bot.message_handler(func=lambda msg: msg.text in buttons['statistics'].values())
def handle_statistics(message):
    Thread(target=handlers.handle_statistics, args=(bot, message)).start()


@bot.message_handler(content_types=['text'])
def handle_text(message):
    Thread(target=handlers.handle_text, args=(bot, message)).start()


@bot.callback_query_handler(func=lambda call: call.data == 'add')
def callback_inline_add(call):
    Thread(target=handlers.callback_inline_add, args=(bot, call)).start()


@bot.callback_query_handler(func=lambda call: 'change_lang' in call.data)
def callback_inline_change_lang(call):
    Thread(target=handlers.callback_inline_change_lang, args=(bot, call)).start()


async def webhook_handle(request):
    if request.path.replace('/', '') == bot.token:
        request_body_dict = await request.json()
        update = Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


def webhook_setup():
    webhook_ssl_cert = 'webhook_cert.pem'
    webhook_ssl_priv = 'webhook_pkey.pem'

    webhook_url_base = f'https://{config.webhook_host}:{config.webhook_port}'
    webhook_url_path = f'/{config.bot_token}/'

    app = web.Application()
    app.router.add_post(f'/{config.bot_token}/', webhook_handle)

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url_base + webhook_url_path, certificate=open(webhook_ssl_cert, 'r'))

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(webhook_ssl_cert, webhook_ssl_priv)

    web.run_app(
        app,
        host=config.webhook_listen,
        port=config.webhook_port,
        ssl_context=context,
    )


if __name__ == '__main__':
    webhook_setup()
