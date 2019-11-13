import datetime
import os
import re
from ast import literal_eval
from random import choice, randint
from time import sleep

import redis
import telegram
from telegram import ParseMode

congrats = (
    ('Oh, shieee...', '*АЛЯРМ*', '*МАЛЬЧИКИ СААБИРИИТЕСЬ!!!*'),
    ('Вычисляем хуевую траекторию...', 'Вычисляем апекс-хуяпекс', '_глубоко затягивает вейп_'),
    ('Вторая группа на старт!', 'Первая группа на старт'),
    ('А Муляр дня сегодня - {}, не вижу нарушения!', '{}, там равных не было, так что ты *Муляр дня* в качестве штрафа',
     'По хуевой траектрии сегодня ездит {}', 'А первое место занимает... мууу... кхм... {}')
)

special = (
    ('Ехал Муляр через Муляр,',),
    ('Видит Муляр - Муляр Муляр.',),
    ('Сунул Муляр Муляр в Муляр,',),
    ('Муляр Муляр Муляр {}',)
)

reminders = (
    'Напоминаю, Муляр дня - {}',
    'Напоминаю, Муляр дня - {}. Прівєт пострижися!'
)

redis_cli = redis.from_url(os.environ.get('REDIS_URL'))


def set_rolled_today(chat_id):
    rec = _get_mulyar_data(str(chat_id))
    rec['updated'] = datetime.date.today().isoformat()
    redis_cli.set(str(chat_id), rec)


def set_winner(chat_id, user_id, name='Муляр'):
    rec = _get_mulyar_data(str(chat_id))
    rec['winner'] = str(user_id)
    rec['custom_name'] = name
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
                       'custom_name': 'Муляр',
                       'updated': '1970-01-01',
                       'winner': ''}
    if user_id not in mulyar_data['pull']:
        mulyar_data['pull'].append(user_id)
        redis_cli.set(str(chat_id), mulyar_data)


def roll_mulyar(bot, update):
    custom_name = 'Муляр'
    if len(update.message.text.split()) > 1:
        regex = re.compile('[^a-zA-Zа-яА-Я0-9 ]')
        custom_name = regex.sub('', ' '.join(update.message.text.split()[1:]))
        if not custom_name.strip():
            custom_name = 'Муляр'
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
        custom_name = md.get('custom_name', 'Муляр')
        bot.send_message(chat_id=chat_id,
                         text=choice(reminders).format(winner).replace('Муляр', custom_name),
                         parse_mode=ParseMode.MARKDOWN)
    else:
        set_rolled_today(chat_id)
        set_winner(chat_id, winner_id, name=custom_name)

        if randint(0, 100) > 79 and len(custom_name) < 50:
            congrats_text = special
        else:
            congrats_text = congrats

        for m in congrats_text:
            bot.send_message(chat_id=chat_id,
                             text=choice(m).format(winner).replace('Муляр', custom_name),
                             parse_mode=ParseMode.MARKDOWN)
            sleep(2)

    add_pipi = not randint(0, 20)
    if add_pipi:
        try:
            bot.send_message(chat_id=chat_id,
                             text='Кстати, Пищинка дня - [{}](tg://user?id={})'.format('Миша', os.environ.get('MISHA_ID')),
                             parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # i don't really give a fuck if this works at all
            pass
