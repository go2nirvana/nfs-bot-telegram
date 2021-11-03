class WeatherException(Exception):
    text = None


class TooFarException(WeatherException):
    text = 'Сорри, прогноз доступен максимум на 15 дней вперед.'


class BadAPIResponse(WeatherException):
    text = 'Чет сервис погоды ругается (или я рак).'


class TypeValidationException(WeatherException):
    text = ("Такого ивента нет. Доступные:\n"
            "`gonzo` - гонзалес\n"
            "`ll` - лайт лига\n"
            "`lch` - лига чемпионов\n"
            "`bg` - БэГэ\n"
            "`day` - прогноз на день\n"
            "`week` - прогноз на неделю")


class APILimitException(WeatherException):
    api_code = 429
    text = 'Лимит запросов исчерпан. Лимиты: 25/ч, 500/день'

    def __init__(self, left_day, left_hour):
        left_text = f'Осталось: {left_hour}/ч, {left_day}/день'
        self.text = '\n'.join([self.text, left_text])
        super().__init__()


class NoBGException(Exception):
    text = 'БэГэ всё:('