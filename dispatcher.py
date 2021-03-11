import datetime
import re
re_location = re.compile(r'([a-яё-]{3,})([a-яё]+$)', re.IGNORECASE)
re_number = re.compile(r'(\+7|8).*?(\d{3}).*?(\d{3}).*?(\d{2}).*?(\d{2})')


class Dispatcher:
    settings = {
        'num_days': 30,
        'daily_tickets': [
            {
                'from_': 'Москва',
                'to_': 'Екатеринбург',
                'when_': (7, 30),
            },
            {
                'from_': 'Москва',
                'to_': 'Владивосток',
                'when_': (6, 40),
            },
            {
                'from_': 'Санкт-Петербург',
                'to_': 'Казань',
                'when_': (8, 35),
            },
            {
                'from_': 'Москва',
                'to_': 'Санкт-Петербург',
                'when_': (13, 15),
            },
            {
                'from_': 'Санкт-Петербург',
                'to_': 'Новосибирск',
                'when_': (17, 20),
            },
            {
                'from_': 'Казань',
                'to_': 'Омск',
                'when_': (21, 00),
            },
            {
                'from_': 'Казань',
                'to_': 'Краснодар',
                'when_': (12, 50),
            },
            {
                'from_': 'Москва',
                'to_': 'Сочи',
                'when_': (5, 00),
            },
        ],
        'tickets_on_weekdays': [
            {
                'from_': 'Москва',
                'to_': 'Пекин',
                'weekdays': (0, 2, 4),
                'when_': (8, 40),
            },
            {
                'from_': 'Санкт-Петербург',
                'to_': 'Токио',
                'weekdays': (0, 2, 3, 6),
                'when_': (6, 5),
            },
            {
                'from_': 'Москва',
                'to_': 'Лондон',
                'weekdays': (0, 2, 4),
                'when_': (10, 30),
            },
            {
                'from_': 'Москва',
                'to_': 'Сан-Франциско',
                'weekdays': (1, 3),
                'when_': (22, 00),
            },
            {
                'from_': 'Москва',
                'to_': 'Париж',
                'weekdays': (0, 3, 5),
                'when_': (12, 00),
            },
            {
                'from_': 'Санкт-Петербург',
                'to_': 'Рим',
                'weekdays': (0, 2, 4),
                'when_': (13, 00),
            },
            {
                'from_': 'Казань',
                'to_': 'Любляна',
                'weekdays': (1, 5),
                'when_': (9, 35),
            },
            {
                'from_': 'Москва',
                'to_': 'Сидней',
                'weekdays': (1, 3),
                'when_': (11, 20),
            },
            {
                'from_': 'Казань',
                'to_': 'Анталья',
                'weekdays': (0, 2, 4),
                'when_': (21, 12),
            },
            {
                'from_': 'Лондон',
                'to_': 'Токио',
                'weekdays': (1, 3),
                'when_': (14, 40),
            },
            {
                'from_': 'Нью-Йорк',
                'to_': 'Гонконг',
                'weekdays': (0, 2, 4),
                'when_': (4, 55),
            }
        ],
        'tickets_on_monthdays': [
            {
                'from_': 'Лондон',
                'to_': 'Бангкок',
                'monthdays': [day_number for day_number in range(1, 31, 2)],
                'when_': (4, 20),
            },
            {
                'from_': 'Новосибирск',
                'to_': 'Париж',
                'monthdays': [day_number for day_number in range(1, 31, 3)],
                'when_': (10, 00),
            }
        ]
    }

    def __init__(self):
        self.available_flights = []
        self.flights = []
        self.flights_to_show = []
        self.tickets = []

    def handle_departure_location(self, from_city):
        daily_flights = Dispatcher.settings['daily_tickets'] + Dispatcher.settings['tickets_on_weekdays'] + \
                        Dispatcher.settings['tickets_on_monthdays']
        match = re.search(re_location, from_city)
        if match:
            user_location = match.group(1)
            for departure in daily_flights:
                if departure['from_'].lower().startswith(user_location):
                    self.available_flights.append(departure)
                elif departure['from_'] == from_city:
                    self.available_flights.append(departure)
        if self.available_flights:
            self.flights.append(from_city)
            return from_city
        else:
            return None

    def handle_arrival_location(self, to_city):
        match = re.search(re_location, to_city)
        if match:
            user_location = match.group(1)
            for arrival in self.available_flights:
                if arrival['to_'].lower().startswith(user_location):
                    self.flights_to_show.append(arrival)
                elif arrival['to_'] == to_city:
                    self.flights_to_show.append(arrival)
        if self.flights_to_show:
            return to_city
        else:
            return None

    def get_date(self, start_date, num_days):
        result = datetime.date(year=start_date.year, month=start_date.month, day=start_date.day) + \
                 datetime.timedelta(days=num_days)
        return result

    def get_time(self, hr_min_tuple):
        result = datetime.time(hour=hr_min_tuple[0], minute=hr_min_tuple[1])
        return result

    def _exemplify_ticket(self, cfg, date):
        time = self.get_time(cfg['when_'])
        ticket = {
            'from_': cfg['from_'],
            'to_': cfg['to_'],
            'when_': datetime.datetime.combine(date, time)
        }
        return ticket

    def date_of_flight(self, start_date):
        start_date = datetime.date(*(int(s) for s in start_date.split('-')))
        num_days = Dispatcher.settings['num_days']
        for cfg in self.flights_to_show:
            if 'monthdays' in cfg:
                for day in range(0, num_days + 1):
                    current_date = self.get_date(start_date, day)
                    monthday_num = current_date.timetuple().tm_mday
                    if monthday_num not in cfg['monthdays']:
                        continue
                    ticket = self._exemplify_ticket(cfg, current_date)
                    self.tickets.append(ticket)
            elif 'weekdays' in cfg:
                for day in range(0, num_days + 1):
                    current_date = self.get_date(start_date, day)
                    weekday_num = current_date.timetuple().tm_wday
                    if weekday_num not in cfg['weekdays']:
                        continue
                    ticket = self._exemplify_ticket(cfg, current_date)
                    self.tickets.append(ticket)
            else:
                for day in range(0, num_days + 1):
                    current_date = self.get_date(start_date, day)
                    ticket = self._exemplify_ticket(cfg, current_date)
                    self.tickets.append(ticket)
        return self.tickets

    def show_flights(self, list_of):
        return list_of


# fin = Dispatcher()