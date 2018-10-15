import json
from ast import literal_eval
from random import choice
from time import sleep

import redis

congrats = (
    ('Oh, shieee...', '*АЛЯРМ*', '*МАЛЬЧИКИ СААБИРИИТЕСЬ!!!*'),
    ('Вычисляем хуевую траекторию...', 'Вычисляем апекс-хуяпекс', '_глубоко затягивает вейп_'),
    ('Вторая группа на старт!', 'Первая группа на старт'),
    ('А Муляр дня сегодня - {}, не вижу нарушения!', '{}, там равных не было, так что *муляр дня* баллов штрафа',
     'По хуевой траектрии сегодня ездит {}', 'А первое место занимает... мууу... кхм... {}')
)


redis_cli = redis.from_url(os.environ.get('REDIS_URL'))
# redis_cli = redis.from_url('redis://h:p2b29026488dbddbb4b61635442d8aa816a68e98d1ceb35b359cfb9beb49e0994@ec2-18-211-154-159.compute-1.amazonaws.com:49039')

if not redis_cli.get('mulyar'):
    redis_cli.set('mulyar', {})


def _get_mulyar_data():
    return literal_eval(redis_cli.get('mulyar').decode())


def accumulate_users(bot, update):
    if update.effective_user.is_bot:
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    mulyar_data = _get_mulyar_data()

    if chat_id in mulyar_data:
        if user_id not in mulyar_data[chat_id]:
            mulyar_data[chat_id].append(user_id)
            redis_cli.set('mulyar', mulyar_data)
    else:
        mulyar_data[chat_id] = [user_id]
        redis_cli.set('mulyar', mulyar_data)


def roll_mulyar(bot, update):
    chat_id = update.effective_chat.id
    md = _get_mulyar_data()
    if not md.get(chat_id):
        return
    winner = choice(md[chat_id])
    winner = bot.get_chat_member(chat_id, winner).user
    print(winner)
    winner = '[{}](tg://user?id={})'.format(' '.join([winner.first_name or '', winner.last_name or '']),
                                            winner.id)
    print(winner)
    if winner:
        for m in congrats:
            bot.send_message(chat_id=chat_id, text=choice(m).format(winner))
            sleep(2)