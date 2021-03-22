import os
from datetime import datetime, timedelta, date, time
from pprint import pprint

import pytz
import requests
from pytz import timezone

from bg_calendar import calendar, get_next_bg

os.environ['TZ'] = 'Europe/Kiev'
request_time_format = '%Y-%m-%dT%H:%M:%S%z'

WEEK_DAYS = 7
monday_i = 0

location_id = os.environ.get('LOCATION_ID')
weather_key = os.environ.get('WEATHER_KEY')

api_url = "https://data.climacell.co/v4/timelines"

weather_fields = [
    'temperatureMin',
    'temperatureMax',
    'temperature',
    'precipitationIntensity',
    'precipitationProbability',
    'weatherCode',
    'precipitationType'
]

common_params = {
    # 'apiKey': weather_key,
    'location': location_id,
    'units': 'metric',
    'timezone': 'Europe/Kiev'
}

events_timesteps = {
    'gonzo': '15m',
    'll': '15m',
    'lch': '15m',
    'bg': '15m',
    'day': '1h',
    'week': '1d',
}

timesteps_length = {
    '15m': 60 * 15,  # 15m
    '1h': 60 * 60,  # 1h
    '1d': 60 * 60 * 24  # 1d
}

events_week_days = {
    'gonzo': 0,  # monday
    'll': 1,  # tuesday
    'lch': 2,  # wednesday
}

events_start_times = {
    'gonzo': (20, 30),
    'll': (20, 30),
    'lch': (20, 30),
    'bg': (10, 00),
    'day': (11, 00),
    'week': (00, 00),
}

availability_hours = {
    '15m': 6,
    '1h': 108,
    '1d': 24 * 15,
}

events_length = {
    'gonzo': 3,
    'll': 3,
    'lch': 3,
    'bg': get_next_bg(datetime.today().date())['length'] + 1,  # add qualifying length
    'day': 11,  # opens at 11, closes at 22
    'week': 7 * 24  # 7 full days
}

event_names = {
    'gonzo': 'Гонзалес',
    'll': 'Лигу Телег',
    'lch': 'Лигу Чемпионов',
    'bg': 'Большие Гонки',
    'day': 'День',
    'week': 'Неделю',
}

too_far_text = 'Сорри, прогноз доступен максимум на 15 дней вперед.'
bad_response_text = 'Чет сервис погоды ругается (или я рак).'


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


class WeatherForecast:
    start_time: datetime
    end_time: datetime

    def __init__(self, event_type):
        self.event_type = event_type
        self.validate_types()
        self.set_times(event_type)
        self.timesteps = self.get_best_timesteps()
        self.adjust_times_to_timestep()

    def validate_types(self):
        if self.event_type in event_names:
            if self.event_type == 'week':
                exc = WeatherException
                exc.text = 'Потом на неделю запилю'
                raise exc
            return
        raise TypeValidationException


    @property
    def event_length(self):
        return events_length[self.event_type]

    @staticmethod
    def get_next_weekday_date(date_: date, weekday: int) -> date:
        return date_ + timedelta(days=(WEEK_DAYS + weekday - date_.weekday()) % WEEK_DAYS)

    def set_times(self, event_type: str):
        now = datetime.now()
        today = now.date()

        if event_type in ('gonzo', 'll', 'lch'):
            start_date = self.get_next_weekday_date(today, events_week_days[event_type])
        elif event_type == 'bg':
            start_date = get_next_bg(today)['date']
        else:  # day or week
            start_date = today

        default_start_datetime = datetime.combine(start_date, time(*events_start_times[event_type]))
        real_start_datetime = now
        self.start_time = max([default_start_datetime, real_start_datetime])
        self.end_time = default_start_datetime + timedelta(hours=self.event_length)

    def get_best_timesteps(self):
        timesteps = ['15m', '1h', '1d']

        days_to_end_time = (self.end_time - datetime.now()).days
        hours_to_end_time = days_to_end_time * 24 + (
                self.end_time - datetime.now()).seconds / 3600  # convert seconds to hours

        for step in timesteps:
            if hours_to_end_time <= availability_hours[step]:
                return step
        else:
            raise TooFarException()

    def adjust_times_to_timestep(self, ):
        days_to_end_time = (self.end_time - datetime.now()).days
        length_seconds = days_to_end_time * 60 * 24 + (
                self.end_time - datetime.now()).seconds  # convert seconds to hours
        if timesteps_length[self.timesteps] <= length_seconds:
            return

        if self.timesteps == '1d':
            self.start_time.replace(hour=0, minute=0)

        end_time = self.start_time + timedelta(**{'1d': {'days': 1},
                                                  '1h': {'hours': 1},
                                                  '15m': {'minutes': 15}}[self.timesteps])

        self.start_time = self.start_time
        self.end_time = end_time

    @staticmethod
    def utc_time_str(dt: datetime):
        return dt.astimezone(pytz.timezone('Europe/Kiev')).strftime(request_time_format)

    def get_request_params(self):
        params = {
            **common_params,
            'timesteps': [self.timesteps],
            'startTime': self.utc_time_str(self.start_time),
            'endTime': self.utc_time_str(self.end_time),
            'fields': weather_fields,
            'timezone': 'Europe/Kiev'
        }
        return params

    def parse_week_forecast(self, data):
        pass

    def parse_detailed_forecast(self, data):
        end_time = self.start_time + timedelta(hours=self.event_length)
        print('DATA', data)
        for item in data:
            dt = datetime.strptime(item['startTime'][:-len(':00')] + '00', request_time_format)
            yield {'time': dt.strftime('%H:%S'),
                   'temperature': f"{round(item['values']['temperature']):+}",
                   'precipitation_amount': round(item['values']['precipitationIntensity'], 2),
                   'precipitation_probability': item['values']['precipitationProbability'],
                   'weather_code': item['values']['weatherCode']}
            print(dt, end_time)
            if dt.replace(tzinfo=None) >= end_time:
                break

    def render_text(self, data):
        pre_header = f"Прогноз на {event_names[self.event_type]} {self.start_time.strftime('%d.%m')}"
        header = f"{'Время': <7}{'Воздух': <7}{'Осадки': <10}"
        line_template = "{time: <7}{temperature: <7}{precipitation_probability}% {precipitation_amount}мм/ч"
        lines = [header, *[line_template.format(**item) for item in data]]
        return ("{pre_header}\n"
                "```\n{forecast}\n```").format(pre_header=pre_header,
                                               forecast='\n'.join(lines))

    def get_forecast(self):
        payload = self.get_request_params()

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", api_url,
                                    params={'apikey': weather_key},
                                    json=payload,
                                    headers=headers)
        print(response.status_code)
        pprint(response.json())

        if response.status_code != 200:
            if response.status_code == APILimitException.api_code:
                headers = response.headers
                exc = APILimitException(headers['X-RateLimit-Remaining-day'],
                                        headers['X-RateLimit-Remaining-hour'])
                raise exc
            else:
                raise BadAPIResponse

        return response.json()['data']['timelines'][0]['intervals']

    def get_bot_response(self):
        data = self.get_forecast()
        if self.timesteps == '1d':
            parsed = self.parse_week_forecast(data)
        else:
            parsed = self.parse_detailed_forecast(data)

        return self.render_text(parsed)

# a = WeatherForecast('gonzo')
# pprint(a.get_bot_response('gonzo'))
