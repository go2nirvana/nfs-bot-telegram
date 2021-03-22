from datetime import datetime

calendar = (
    {'date': '17.04.2021',
     'length': 4},
    {'date': '01.05.2021',
     'length': 4},
    {'date': '15.05.2021',
     'length': 7},
    {'date': '29.05.2021',
     'length': 4},
    {'date': '12.06.2021',
     'length': 4},
    {'date': '26.06.2021',
     'length': 7},
    {'date': '10.07.2021',
     'length': 4},
    {'date': '24.07.2021',
     'length': 4},
    {'date': '07.08.2021',
     'length': 7},
    {'date': '21.08.2021',
     'length': 4},
    {'date': '04.09.2021',
     'length': 4},
    {'date': '18.09.2021',
     'length': 7},
    {'date': '02.10.2021',
     'length': 4},
    {'date': '16.10.2021',
     'length': 4},
    {'date': '30.10.2021',
     'length': 10}
)

for item in calendar:
    item['date'] = datetime.strptime(item['date'], '%d.%m.%Y').date()


def get_next_bg(date_):
    for item in calendar:
        if item['date'] >= date_:
            return item
