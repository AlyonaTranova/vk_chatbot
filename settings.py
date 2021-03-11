# Use your token and group id
TOKEN = ''
GROUP_ID = 

INTENTS = [
    {
        "name": 'Выбор билета',
        "tokens": {'/ticket'},
        "scenario": 'ticket_choice',
        "answer": None,
    },
    {
        "name": 'Помощь',
        "tokens": {'/help'},
        "scenario": None,
        "answer": 'Для того, чтобы начать выбор билета - введите "/ticket". Далее Вам нужно будет ввести пункт город '
                  'отправления и назначения, а также детали поездки и Ваш номер телефона, чтобы мы смогли с Вами '
                  'связаться. '
    }
]

SCENARIOS = {
    'ticket_choice': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Введите город отправления',
                'failure_text': 'Ошибка - попробуйте ввести название города еще раз',
                'handler': 'handle_departure_city',
                'next_step': 'step2'
            },
            'step2': {
                'text': 'Введите город назначения',
                'failure_text': 'К сожалению, вылет в данное назначение недоступен',
                'handler': 'handle_arrival_city',
                'next_step': 'step3'
            },
            'step3': {
                'text': 'Введите желаемую дату вылета в формате гггг-мм-дд',
                'failure_text': 'Ошибка - неправильная дата, введите еще раз',
                'handler': 'handle_date',
                'next_step': 'step4'
            },
            'step4': {
                'text': 'Выберите предпочтительный рейс из указанных: \n {flights_as_str}\n',
                'failure_text': 'Рейса с таким номером нет, попробуйте еще раз',
                'handler': 'choose_the_flight',
                'next_step': 'step5'
            },
            'step5': {
                'text': 'Вы выбрали {chosen_flight}. Введите количество требуемых билетов (от 1 до 5)',
                'failure_text': 'Ошибка',
                'handler': 'handle_quantity',
                'next_step': 'step6'
            },
            'step6': {
                'text': 'Комментарий к заказу: ',
                'failure_text': None,
                'handler': 'handle_comment',
                'next_step': 'step7'
            },
            'step7': {
                'text': 'Ваши данные:\n {summary}\n  Всё верно? Введите да/нет',
                'failure_text': 'Ошибка - введите да/нет',
                'handler': 'handle_answer',
                'next_step': 'step8'
            },
            'step8': {
                'text': 'Введите номер телефона в формате +7ХХХХХХХХХ, чтобы мы могли с Вами связаться',
                'failure_text': 'Неправильный формат телефона, попробуйте ввести еще раз',
                'handler': 'handle_number',
                'next_step': 'step9'
            },
            'step9': {
                'text': 'Спасибо! Ваш запрос принят в обработку, '
                        'мы свяжемся с вами в ближайшее время по {number} номеру',
                'image': 'generate_image',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    }
}

DEFAULT_ANSWER = 'Я не знаю, как на это ответить. Введите /ticket для выбора билета, либо /help для справки'

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    host='localhost',
    database='vk_chat_bot'
)
