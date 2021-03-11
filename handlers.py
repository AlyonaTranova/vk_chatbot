import datetime
import re
from collections import defaultdict
from pprint import pprint
from dispatcher import Dispatcher
from generate_ticket import generate_ticket

re_location = re.compile(r'([a-яё-]{3,})([a-яё]+$)', re.IGNORECASE)
re_number = re.compile(r'(\+7|8).*?(\d{3}).*?(\d{3}).*?(\d{2}).*?(\d{2})')
disp = Dispatcher()


# step 1
def handle_departure_city(text, context):
    checked_answer = disp.handle_departure_location(from_city=text)
    if checked_answer is not None:
        context['from'] = text
        return True
    else:
        return False


# step 2
def handle_arrival_city(text, context):
    checked_answer = disp.handle_arrival_location(to_city=text)
    if checked_answer is not None:
        context['to'] = text
        return True
    elif checked_answer is None:
        return False


# step 3
def handle_date(text, context):
    try:
        checked_text = datetime.datetime.strptime(text, '%Y-%m-%d')
    except ValueError:
        return False
    now = datetime.datetime.now()
    if checked_text < datetime.datetime(year=now.year, month=now.month, day=now.day):
        return False
    else:
        context['date'] = text
        date_flights = disp.date_of_flight(start_date=context['date'])
        flights = disp.show_flights(list_of=date_flights)
        context['flights'] = str(flights)
        context['flights_as_str'] = get_flights_as_str(flights)
        return True


# step 4
def choose_the_flight(text, context):
    if text.isdigit():
        available_flights = disp.date_of_flight(start_date=context['date'])
        print(available_flights)
        if int(text) <= len(available_flights):
            reis = available_flights[int(text)]
            context['date_of_flight'] = str(reis['when_'])
            context['city_of_departure'] = reis["from_"]
            context['city_of_arrival'] = reis["to_"]
            context['chosen_flight'] = int(text)
            return True
    else:
        return False


# step 5
def handle_quantity(text, context):
    if text.isdigit():
        if 1 <= int(text) <= 5:
            context['ticket_quantity'] = text
            return True
    else:
        return False


# step 6
def handle_comment(text, context):
    context['comment'] = text
    context['summary'] = show_the_data(context)
    return True


# step 7
def show_the_data(context):
    summary = {'Город вылета': context['city_of_departure'], 'Город прибытия': context['city_of_arrival'],
               'Дата и время вылета': context['date_of_flight'], 'Кол-во билетов': context['ticket_quantity'],
               'Комментарий к заказу': context['comment']}
    result = ''
    for key, value in summary.items():
        result += f'{key}: {value}\n'
    return result


# step 7
def handle_answer(text, context):
    text = text.lower()
    if text == 'да':
        return True
    elif text == 'нет':
        context['quit_message'] = 'Вы выбрали завершить оформление билета.'
    else:
        return False


# step 8
def handle_number(text, context):
    match = re.match(re_number, text)
    if match:
        context['number'] = text
        return True
    else:
        return False


def get_flights_as_str(flights):
    result = ''
    for index, flight in enumerate(flights, start=1):
        result += f'{index}: {flight["from_"]} -> {flight["to_"]}, {str(flight["when_"])}\n'
    return result


def generate_image(text, context):
    return generate_ticket(departure=context['city_of_departure'], arrival=context['city_of_arrival'],
                           date=context['date_of_flight'], quantity=context['ticket_quantity'],
                           number=context['number'])
