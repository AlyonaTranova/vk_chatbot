import _io
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock, ANY
from generate_ticket import generate_ticket
from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEvent
import settings
from bot import Bot
from freezegun import freeze_time
import handlers
import os
from io import BytesIO
from random import *
from PIL import Image, ImageDraw, ImageFont


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()

    return wrapper


class Test1(TestCase):
    RAW_EVENT = {'type': 'message_new', 'object':
        {'message': {'date': 1611510231, 'from_id': 88944328, 'id': 53, 'out': 0, 'peer_id': 88944328,
                     'text': 'h', 'conversation_message_id': 51, 'fwd_messages': [], 'important': False, 'random_id': 0,
                     'attachments': [], 'is_hidden': False}, 'client_info': {'button_actions':
                                                                                 ['text', 'vkpay', 'open_app',
                                                                                  'location', 'open_link',
                                                                                  'intent_subscribe',
                                                                                  'intent_unsubscribe'],
                                                                             'keyboard': True, 'inline_keyboard': True,
                                                                             'carousel': False, 'lang_id': 0}},
                 'group_id': 201846010, 'event_id': '6ff5bc3d240b8b61ca2a82faa6227ba8cfdad5d9'}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.vk_api.bot_longpoll.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                bot.on_event.call_count == count

    INPUTS = [
        'Привет',
        '/help',
        '/ticket',
        'Москва',
        'Лондон',
        '12-05-2021',
        '2021-04-12',
        '7',
        '3',
        'комментарий',
        'да',
        '+79504238676',
    ]

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['ticket_choice']['steps']['step1']['text'],
        settings.SCENARIOS['ticket_choice']['steps']['step2']['text'],
        settings.SCENARIOS['ticket_choice']['steps']['step3']['text'],
        settings.SCENARIOS['ticket_choice']['steps']['step3']['failure_text'],
        settings.SCENARIOS['ticket_choice']['steps']['step4']['text'].format(
            flights_as_str='1: Москва -> Лондон, 2021-04-12 10:30:00\n2: Москва -> Лондон, 2021-04-14 10:30:00\n'
                           '3: Москва -> Лондон, 2021-04-16 10:30:00\n4: Москва -> Лондон, 2021-04-19 10:30:00\n'
                           '5: Москва -> Лондон, 2021-04-21 10:30:00\n6: Москва -> Лондон, 2021-04-23 10:30:00\n'
                           '7: Москва -> Лондон, 2021-04-26 10:30:00\n8: Москва -> Лондон, 2021-04-28 10:30:00\n'
                           '9: Москва -> Лондон, 2021-04-30 10:30:00\n10: Москва -> Лондон, 2021-05-03 10:30:00\n'
                           '11: Москва -> Лондон, 2021-05-05 10:30:00\n12: Москва -> Лондон, 2021-05-07 10:30:00\n'
                           '13: Москва -> Лондон, 2021-05-10 10:30:00\n14: Москва -> Лондон, 2021-05-12 10:30:00\n'),
        settings.SCENARIOS['ticket_choice']['steps']['step5']['text'].format(
            chosen_flight='7'),
        settings.SCENARIOS['ticket_choice']['steps']['step6']['text'],
        settings.SCENARIOS['ticket_choice']['steps']['step7']['text'].format(
            summary="Город вылета: Москва\nГород прибытия: Лондон\nДата и время вылета: 2021-04-28 10:30:00\n"
                    "Кол-во билетов: 3\nКомментарий к заказу: комментарий\n"),
        settings.SCENARIOS['ticket_choice']['steps']['step8']['text'],
        settings.SCENARIOS['ticket_choice']['steps']['step9']['text'].format(number='+79504238676')
    ]

    @isolate_db
    @freeze_time("Jan 16th, 2021")
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.vk_api.bot_longpoll.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        for real, expec in zip(real_outputs, self.EXPECTED_OUTPUTS):
            print(real)
            print('-' * 50)
            print(expec)
            print('-' * 50)
            print(real == expec)
            print('_' * 50)

        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image(self):
        result_image = generate_ticket(departure='Москва', arrival='Лондон', date='2021-12-12 10:00', quantity='2',
                                       number='+79099671212')

        test_image = Image.open('files/test_image.png')
        test = _io.BytesIO()
        test_image.save(test, 'png')
        print(type(result_image), type(test))
        self.assertEqual(type(result_image), type(test))
