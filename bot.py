import logging

import os
import re
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from mulyar import accumulate_users, roll_mulyar

nfs_chat_id = os.environ.get('NFS_CHAT_ID')
admin_chat_id = os.environ.get('ADMIN_CHAT_ID')

updater = Updater(token=os.environ.get('BOT_TOKEN'))

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

tracks_videos = {
    '1': 'https://www.youtube.com/watch?v=bgjPhZoP-hg',
    '2': 'https://www.youtube.com/watch?v=4ztokJHdZCA\nhttps://youtu.be/CSOsdOCMA8U\nhttps://youtu.be/L2zLjuYXqLM',
    '3r': 'https://www.youtube.com/watch?v=gJYpIeA-DXI',
    '4r': 'https://www.youtube.com/watch?v=1jEUzqv9HTI',
    '5r': 'https://www.youtube.com/watch?v=TCX2fkVBXXo',
    '7': 'https://www.youtube.com/watch?v=PS4YyPBjdGk',
    '7r': 'https://www.youtube.com/watch?v=1vN8BeDobmo',
    '10': 'https://www.youtube.com/watch?v=wjEatid4OrY',
    '9': 'https://www.youtube.com/watch?v=Qxtm6zpcB-s\nhttps://www.youtube.com/watch?v=NLZmBhHZI4U',
    '9r': 'https://www.youtube.com/watch?v=UCNhStrNAEc',
    '11r': 'https://www.youtube.com/watch?v=lrc-jDG8Z0Y\nhttps://www.youtube.com/watch?v=lrc-jDG8Z0Y',

}


def track_light(bot, update):
    pass


def track_champ(bot, update):
    pass


def config_handler(bot, update):
    try:
        config_number = re.findall(r'/config (\d+[r]?)', update.message.text.lower())[0]
        is_correct = config_number in {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                                       '1r', '2r', '3r', '4r', '5r', '6r', '7r', '8r', '9r', '10r', '11r'}
    except IndexError:
        is_correct = False

    if is_correct:
        video_url = tracks_videos.get(config_number, 'Видео нет :(')
        response = 'Карта конфига *№{}:*\n{}'.format(
            config_number.replace('r', ' РЕВЕРС'),
            video_url)
        bot.send_message(chat_id=update.message.chat_id,
                         text=response,
                         parse_mode=ParseMode.MARKDOWN,
                         disable_web_page_preview=True)
        if config_number not in {'1r', '2r', '3r'}:
            config_number = config_number.replace('r', '')
        bot.send_photo(chat_id=update.message.chat_id,
                       photo=open('tracks/%s.png' % config_number, 'rb'))
    else:
        response = 'Такого конфига нет'
        bot.send_message(chat_id=update.message.chat_id, text=response)


def say(bot, update):
    if update.effective_chat.id == admin_chat_id:
        msg = update.message.text.lower()[5:]
        bot.send_message(chat_id=nfs_chat_id, text=msg)


def week_handler(bot, update):
    pass


def month_handler(bot, update):
    pass


dispatcher.add_handler(MessageHandler(Filters.text, accumulate_users))
dispatcher.add_handler(CommandHandler('track_light', track_light))
dispatcher.add_handler(CommandHandler('track_champ', track_champ))
dispatcher.add_handler(CommandHandler('config', config_handler))
dispatcher.add_handler(CommandHandler('week', week_handler))
dispatcher.add_handler(CommandHandler('month', month_handler))
dispatcher.add_handler(CommandHandler('moo', roll_mulyar))
dispatcher.add_handler(CommandHandler('say', say))

updater.start_polling()
