import logging

import os
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

updater = Updater(token=os.environ.get('BOT_TOKEN'))
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def track_light(bot, update):
    pass


def track_champ(bot, update):
    pass


def config_handler(bot, update):
    config_number = update.message.text[len('/config'):].strip().lower()
    is_correct = config_number in {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                                   '1r', '2r', '3r', '4r', '5r', '6r', '7r', '8r', '9r', '10r', '11r'}
    if is_correct:
        is_reverse = config_number.endswith('r')
        if is_reverse:
            config_number = config_number[:-1]
        response = 'Карта конфига *№{}{}:*'.format(config_number, ' РЕВЕРС' if is_reverse else '')
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode=ParseMode.MARKDOWN)

        photo_name = config_number + ('r' if is_reverse and config_number in '123' else '') + '.png'
        bot.send_photo(chat_id=update.message.chat_id,
                       photo=open('tracks/%s' % photo_name, 'rb'))
    else:
        response = 'Такого конфига нет'
        bot.send_message(chat_id=update.message.chat_id, text=response)



def week_handler(bot, update):
    pass


def month_handler(bot, update):
    pass


dispatcher.add_handler(CommandHandler('track_light', track_light))
dispatcher.add_handler(CommandHandler('track_champ', track_champ))
dispatcher.add_handler(CommandHandler('config', config_handler))
dispatcher.add_handler(CommandHandler('week', week_handler))
dispatcher.add_handler(CommandHandler('month', month_handler))

updater.start_polling()
