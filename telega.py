import os
from ast import literal_eval

import redis
import telegram
from telegram import ParseMode

redis_cli = redis.from_url(os.environ.get('REDISCLOUD_URL'))


def get_chat_telegas(chat_id):
    res = redis_cli.get(str(chat_id))
    res = literal_eval(res.decode()) if res else None
    return res.get('telegas')


def add_telega(chat_id, user_id):
    res = redis_cli.get(str(chat_id))
    res = literal_eval(res.decode()) if res else None
    if 'telegas' not in res:
        res['telegas'] = []
    telegas = res['telegas']
    if not telegas or telegas[-1] != user_id:
        telegas.append(user_id)
        if len(telegas) > 2:
            telegas = telegas[1:3]
    res['telegas'] = telegas
    redis_cli.set(str(chat_id), res)


def get_next_telega(chat_id, caller_id):
    add_telega(chat_id, caller_id)
    chat_telegas = get_chat_telegas(chat_id)
    return chat_telegas[0]


def notime(bot, update):
    if update.effective_user.is_bot:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    telega_id = get_next_telega(chat_id, user_id)

    try:
        telega_user = bot.get_chat_member(chat_id, telega_id).user
    except telegram.error.BadRequest:
        bot.send_message(chat_id=chat_id,
                         text='Чот не получилось :С',
                         parse_mode=ParseMode.MARKDOWN)
        return

    telega_tag = '[{}](tg://user?id={})'.format(' '.join([telega_user.last_name or telega_user.first_name]),
                                                telega_user.id)

    bot.send_message(chat_id=update.message.chat_id,
                     text="{} - телега:)".format(telega_tag),
                     parse_mode=ParseMode.MARKDOWN)
