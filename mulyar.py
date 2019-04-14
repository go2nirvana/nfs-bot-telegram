import datetime
import os
from ast import literal_eval
from random import choice
from time import sleep

import redis
import telegram
from telegram import ParseMode

congrats = (
    ('Oh, shieee...', '*АЛЯРМ*', '*МАЛЬЧИКИ СААБИРИИТЕСЬ!!!*'),
    ('Вычисляем хуевую траекторию...', 'Вычисляем апекс-хуяпекс', '_глубоко затягивает вейп_'),
    ('Вторая группа на старт!', 'Первая группа на старт'),
    ('А Муляр дня сегодня - {}, не вижу нарушения!', '{}, там равных не было, так что ты *муляр дня* в качестве штрафа',
     'По хуевой траектрии сегодня ездит {}', 'А первое место занимает... мууу... кхм... {}')
)

redis_cli = redis.from_url(os.environ.get('REDIS_URL'))


def set_rolled_today(chat_id):
    rec = _get_mulyar_data(str(chat_id))
    rec['updated'] = datetime.date.today().isoformat()
    redis_cli.set(str(chat_id), rec)


def set_winner(chat_id, user_id):
    rec = _get_mulyar_data(str(chat_id))
    rec['winner'] = str(user_id)
    redis_cli.set(str(chat_id), rec)


def is_rolled_today(chat_id):
    rec = _get_mulyar_data(str(chat_id))
    return rec['updated'] == datetime.date.today().isoformat()


def _get_mulyar_data(chat_id):
    res = redis_cli.get(str(chat_id))
    return literal_eval(res.decode()) if res else None


def accumulate_users(bot, update):
    if update.effective_user.is_bot:
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    mulyar_data = _get_mulyar_data(chat_id)
    if not mulyar_data:
        mulyar_data = {'pull': [],
                       'updated': '1970-01-01',
                       'winner': ''}
    if user_id not in mulyar_data['pull']:
        mulyar_data['pull'].append(user_id)
        redis_cli.set(str(chat_id), mulyar_data)


def roll_mulyar(bot, update):
    chat_id = update.effective_chat.id
    md = _get_mulyar_data(chat_id)
    if not md:
        return

    retries = 0
    while True:
        try:
            winner_id = choice(md['pull']) if not is_rolled_today(chat_id) else md['winner']
            winner = bot.get_chat_member(chat_id, winner_id).user
            break
        except telegram.error.BadRequest:
            retries += 1
            if retries > 10:
                bot.send_message(chat_id=chat_id,
                                 text='Чот не получилось :С',
                                 parse_mode=ParseMode.MARKDOWN)
                return

    winner = '[{}](tg://user?id={})'.format(' '.join([winner.first_name or '', winner.last_name or '']),
                                            winner.id)
    if is_rolled_today(chat_id):
        bot.send_message(chat_id=chat_id,
                         text='Напоминаю, муляр дня - {}'.format(winner),
                         parse_mode=ParseMode.MARKDOWN)
        return
    set_rolled_today(chat_id)
    set_winner(chat_id, winner_id)
    for m in congrats:
        bot.send_message(chat_id=chat_id,
                         text=choice(m).format(winner),
                         parse_mode=ParseMode.MARKDOWN)
        sleep(2)