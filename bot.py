# -*- coding: utf-8 -*- 

import telebot
from telebot import types

import json
import urllib.parse
from urllib.request import urlopen

from defines import *
from stats import *
from rate_limiter import RateLimiter


bot = telebot.TeleBot(token=BOT_TOKEN, threaded=False)

rate_limiter = RateLimiter()

class FakeChat:
    def __init__(self, chat_id):
        self.id = chat_id

class FakeMessage:
    def __init__(self, chat_id):
        self.chat = FakeChat(chat_id)

db_manager = SimpleDbManager(DB_NAME)

# this dictionary has key=source_identifier and value=list where
# list contains 5 elements:
# - source_url
# - getter_function (use to load data from MinCult)
# - slicer funciton (use to slice some data)
# - category 1 (required)
# - category 2 (optional)
events_info = {}

def add_row_to_event_info(identifier, url, getter, slicer, cat1, cat2=None):
    events_info[identifier] = [url, getter, slicer, cat1, cat2]

def get_url_for_identifier(source_identifier):
    return events_info[source_identifier][0]

def get_getter_for_identifier(source_identifier):
    return events_info[source_identifier][1]

def get_slicer_for_identifier(source_identifier):
    return events_info[source_identifier][2]

def get_cat1_for_identifier(source_identifier):
    return events_info[source_identifier][3]

def get_cat2_for_identifier(source_identifier):
    return events_info[source_identifier][4]

def initialize():
    add_row_to_event_info(FILMS_IDENTIFIER, FILMS_URL, get_list_of_events, get_slice_of_events, "Film_screening")
    add_row_to_event_info(LECTURES_IDENTIFIER, LECTURES_URL, get_list_of_events, get_slice_of_events, "Lectures")

    # Performances
    add_row_to_event_info(TRAGICOMEDY_IDENTIFIER, TRAGICOMEDY_URL, get_list_of_events, get_slice_of_events, "Performances", "Tragicomedy")
    add_row_to_event_info(MODERN_ART_IDENTIFIER, MODERN_ART_URL, get_list_of_events, get_slice_of_events, "Performances", "Modern_art")
    add_row_to_event_info(CLASSIC_ART_IDENTIFIER, CLASSIC_ART_URL, get_list_of_events, get_slice_of_events, "Performances", "Classical_art")
    add_row_to_event_info(DRAMA_IDENTIFIER, DRAMA_URL, get_list_of_events, get_slice_of_events, "Performances", "Drama")
    add_row_to_event_info(COMEDY_IDENTIFIER, COMEDY_URL, get_list_of_events, get_slice_of_events, "Performances", "Comedy")
    add_row_to_event_info(BALLET_IDENTIFIER, BALLET_URL, get_list_of_events, get_slice_of_events, "Performances", "Ballet")
    add_row_to_event_info(MONOSPECT_IDENTIFIER, MONOSPECT_URL, get_list_of_events, get_slice_of_events, "Performances", "Monospect")
    add_row_to_event_info(EXP_THEATRE_IDENTIFIER, EXP_THEATRE_URL, get_list_of_events, get_slice_of_events, "Performances", "Experimental_theatre")
    add_row_to_event_info(PUPPET_SHOW_IDENTIFIER, PUPPET_SHOW_URL, get_list_of_events, get_slice_of_events, "Performances", "Puppet_show")
    add_row_to_event_info(FOLKLORE_IDENTIFIER, FOLKLORE_URL, get_list_of_events, get_slice_of_events, "Performances", "Folklore")

    # Concerts
    add_row_to_event_info(OPERA_IDENTIFIER, OPERA_URL, get_list_of_events, get_slice_of_events, "Concerts", "Opera")
    add_row_to_event_info(CLASSIC_MUSIC_IDENTIFIER, CLASSIC_MUSIC_URL, get_list_of_events, get_slice_of_events, "Concerts", "Classical_music")
    add_row_to_event_info(FOLKLORE_MUSIC_IDENTIFIER, FOLKLORE_MUSIC_URL, get_list_of_events, get_slice_of_events, "Concerts", "Folklore_music")
    add_row_to_event_info(JAZZ_IDENTIFIER, JAZZ_URL, get_list_of_events, get_slice_of_events, "Concerts", "Jazz")
    add_row_to_event_info(ORGAN_MUSIC_IDENTIFIER, ORGAN_MUSIC_URL, get_list_of_events, get_slice_of_events, "Concerts", "Organ_music")
    add_row_to_event_info(AUTHOR_SONG_IDENTIFIER, AUTHOR_SONG_URL, get_list_of_events, get_slice_of_events, "Concerts", "Author_song")

    # Exhibitions
    add_row_to_event_info(MODERN_ART_EXHIBIT_IDENTIFIER, MODERN_ART_EXHIBIT_URL, get_list_of_events, get_slice_of_events, "Exhibitions", "Modern_art_exhibit")
    add_row_to_event_info(PHOTO_IDENTIFIER, PHOTO_URL, get_list_of_events, get_slice_of_events, "Exhibitions", "Photo")
    add_row_to_event_info(GRAPHIC_IDENTIFIER, GRAPHIC_URL, get_list_of_events, get_slice_of_events, "Exhibitions", "Graphic")
    add_row_to_event_info(PAINTING_IDENTIFIER, PAINTING_URL, get_list_of_events, get_slice_of_events, "Exhibitions", "Painting")
    add_row_to_event_info(DESIGN_IDENTIFIER, DESIGN_URL, get_list_of_events, get_slice_of_events, "Exhibitions", "Design")
    add_row_to_event_info(SCULPTURE_IDENTIFIER, SCULPTURE_URL, get_list_of_events, get_slice_of_events, "Exhibitions", "Sculpture")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Выставки \U0001F3A8',
            'Спектакли \U0001F3AD',
            'Концерты \U0001F3BC',
            'Кинопоказ \U0001F4FA',
            'Лекции \U0001F4DA')

    if not rate_limiter.can_send_to(message.chat.id):
        update_drop_msg()
        return

    update_sent_msg()
    next_step = bot.send_message(message.chat.id,
            'Выберете интересующее вас направление.',
            reply_markup=markup)
    rate_limiter.send_to(message.chat.id)
    bot.register_next_step_handler(next_step, process_main_step)

def check_none(input, key, index=-1, subkey=""):
    if key in input:
        if index == -1:
            return input[key]
        if len(input) > index:
            if subkey == "":
                return input[key][index]
            return input[key][index][subkey]

    return ''

def do_urlopen(url):
    try:
        resp = urlopen(url=url, timeout=MIN_CULT_TIMEOUT)
        return resp
    except:
        print("urlopen() for url={} failed".format(url))
        return None

def get_list_of_events(url):
    resp = do_urlopen(url)
    if not resp:
        return resp

    events = json.loads(resp.read().decode('utf8'))

    events_list = []
    for event in events['events']:
        # NOTE: we use only first place for 'place' and 'address', maybe it's wrong
        # The same case for 'url'
        events_list.append({'name': check_none(event, 'name'), 'place': check_none(event, 'places', 0),
                            'address': check_none(event, 'places', 0, 'address'),
                            'shortDescription': check_none(event, 'shortDescription'),
                            'ext_info': check_none(event, 'externalInfo', 0)})

    return events_list


def get_slice_of_events(events_list, start, stop):
    result = ''

    for event in events_list[start : stop]:
        name = '*' + event['name'] + '*' + '\n\n'
        place = ''
        if('name' in event['place']):
            place = 'Место проведения: ' + event['place']['name'] + '\n\n'
        address = ''
        if('source' in event['address']):
            address = 'Адрес: ' + event['address']['source'] + '\n\n'
        short_desc = 'Краткое описание: ' + event['shortDescription'] + '\n\n'
        show_url = ''
        if('url' in event['ext_info']):
            show_url = 'Подробнее: [' + event['ext_info']['url'] + ']\n\n'
        result += name + place + address + short_desc + show_url + '\n\n'

    return result


def make_inline_buttons(start, stop, source_len, source_identifier):
    keyboard = types.InlineKeyboardMarkup()

    btns = []
    if start > 0:
        btns.append(types.InlineKeyboardButton(
            text='\U00002B05', callback_data='{}_{}'.format(source_identifier, start - PAGE_STEP)))
    if stop < source_len:
        btns.append(types.InlineKeyboardButton(
            text='\U000027A1', callback_data='{}_{}'.format(source_identifier, stop)))
    keyboard.add(*btns)

    return keyboard


@bot.callback_query_handler(func=lambda c: c.data)
def do_pagination(c):
    parts = c.data.split('_')
    if len(parts) != 2:
        print("invalid data in callback query handler")
        return

    source_identifier = int(parts[0])
    print('received source_identifier {}'.format(source_identifier))
    if not source_identifier in events_info:
        print("invalid identifier in callback query handler")
        return

    offset = int(parts[1])
    # prepare data for source_identifier
    event_url = get_url_for_identifier(source_identifier)
    events_list = get_getter_for_identifier(source_identifier)(event_url)
    if events_list:
        text = get_slicer_for_identifier(source_identifier)(events_list, offset, offset + PAGE_STEP)
        # send data to user
        try:
            update_sent_msg()
            bot.edit_message_text(
                chat_id = c.message.chat.id,
                message_id = c.message.message_id,
                text = text,
                parse_mode = 'Markdown',
                reply_markup = make_inline_buttons(offset, offset + PAGE_STEP, len(events_list), source_identifier))
        except:
            print('edit_message() failed')
    else:
        text = MIN_CULT_CONNECTION_ERROR
        update_sent_msg()
        bot.send_message(chat_id=c.message.chat.id, text=text)

def process_main_step(message):
    chat_id = message.chat.id
    username = message.chat.username

    if message.text=='Спектакли \U0001F3AD':
        print('Performances')
        db_manager.add_record(username, "Performances")

        markup = types.ReplyKeyboardMarkup()
        item1 = types.KeyboardButton('Современное искусство')
        item2= types.KeyboardButton("Классическое искусство")
        item3 = types.KeyboardButton("Трагикомедия")
        item4 = types.KeyboardButton("Драма")
        item5 = types.KeyboardButton("Комедия")
        item6 = types.KeyboardButton('Балет')
        item7 = types.KeyboardButton("Моноспектакль")
        item8 = types.KeyboardButton("Эксперементальный театр")
        item9 = types.KeyboardButton("Кукольный спектакль")
        item10 = types.KeyboardButton("Фольклор")
        item = types.KeyboardButton('Главное меню')

        markup.row(item1)
        markup.row(item2)
        markup.row(item3)
        markup.row(item4)
        markup.row(item5)
        markup.row(item6)
        markup.row(item7)
        markup.row(item8)
        markup.row(item9)
        markup.row(item10)
        markup.row(item)

        if not rate_limiter.can_send_to(message.chat.id):
            update_drop_msg()
            fake_step = FakeMessage(message.chat.id)
            bot.register_next_step_handler(fake_step, process_main_step)
            return

        update_sent_msg()
        next_step = bot.send_message(message.chat.id,
                'Какое направление предпочитаете? \nДля полного списка прокрутите вниз!', reply_markup=markup)
        rate_limiter.send_to(message.chat.id)
        bot.register_next_step_handler(next_step, process_step_2)

    elif message.text==('Кинопоказ \U0001F4FA'):
        print('Film screening')
        db_manager.add_record(username, get_cat1_for_identifier(FILMS_IDENTIFIER))
        make_first_answer(FILMS_IDENTIFIER, chat_id, process_main_step)

    elif message.text==('Лекции \U0001F4DA'):
        print('Lectures')
        db_manager.add_record(username, get_cat1_for_identifier(LECTURES_IDENTIFIER))
        make_first_answer(LECTURES_IDENTIFIER, chat_id, process_main_step)

    elif message.text=='Концерты \U0001F3BC':
        print('Concerts')
        db_manager.add_record(username, "Concerts")

        markup = types.ReplyKeyboardMarkup()
        item1 = types.KeyboardButton("Опера")
        item2 = types.KeyboardButton("Классическая музыка")
        item3 = types.KeyboardButton("Фольклорная музыка")
        item4 = types.KeyboardButton("Джаз")
        item5 = types.KeyboardButton("Органная музыка")
        item6 = types.KeyboardButton("Авторская песня")
        item =  types.KeyboardButton('Главное меню')

        markup.row(item1)
        markup.row(item2)
        markup.row(item3)
        markup.row(item4)
        markup.row(item5)
        markup.row(item6)
        markup.row(item)

        if not rate_limiter.can_send_to(message.chat.id):
            update_drop_msg()
            fake_step = FakeMessage(message.chat.id)
            bot.register_next_step_handler(fake_step, process_main_step)
            return

        update_sent_msg()
        next_step = bot.send_message(message.chat.id,
                'Какое направление предпочитаете? \nДля полного списка прокрутите вниз!',
                reply_markup=markup)
        rate_limiter.send_to(message.chat.id)
        bot.register_next_step_handler(next_step, process_step_2)

    elif message.text=='Выставки \U0001F3A8':
        print('Exhibitions')
        db_manager.add_record(username, "Exhibitions")

        markup = types.ReplyKeyboardMarkup()
        item1 = types.KeyboardButton("Современное Искусство")
        item2 = types.KeyboardButton("Фотография")
        item3 = types.KeyboardButton("Графика")
        item4 = types.KeyboardButton("Живопись")
        item5 = types.KeyboardButton("Дизайн")
        item6 = types.KeyboardButton("Скульптура")
        item =  types.KeyboardButton('Главное меню')

        markup.row(item1)
        markup.row(item2)
        markup.row(item3)
        markup.row(item4)
        markup.row(item5)
        markup.row(item6)
        markup.row(item)

        if not rate_limiter.can_send_to(message.chat.id):
            update_drop_msg()
            fake_step = FakeMessage(message.chat.id)
            bot.register_next_step_handler(fake_step, process_main_step)
            return

        update_sent_msg()
        next_step = bot.send_message(message.chat.id,
                'Какое направление предпочитаете? \n Для полного списка прокрутите вниз!',
                reply_markup=markup)
        rate_limiter.send_to(message.chat.id)
        bot.register_next_step_handler(next_step, process_step_2)


def process_step_2(message):
    chat_id = message.chat.id
    username = message.chat.username

    # this is performance
    if message.text==("Трагикомедия"):
        db_manager.add_record(username, get_cat1_for_identifier(TRAGICOMEDY_IDENTIFIER), get_cat2_for_identifier(TRAGICOMEDY_IDENTIFIER))
        make_first_answer(TRAGICOMEDY_IDENTIFIER, chat_id, process_step_2)
    elif message.text==("Современное искусство"):
        db_manager.add_record(username, get_cat1_for_identifier(MODERN_ART_IDENTIFIER), get_cat2_for_identifier(MODERN_ART_IDENTIFIER))
        make_first_answer(MODERN_ART_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Классическое искусство'):
        db_manager.add_record(username, get_cat1_for_identifier(CLASSIC_ART_IDENTIFIER), get_cat2_for_identifier(CLASSIC_ART_IDENTIFIER))
        make_first_answer(CLASSIC_ART_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Драма'):
        db_manager.add_record(username, get_cat1_for_identifier(DRAMA_IDENTIFIER), get_cat2_for_identifier(DRAMA_IDENTIFIER))
        make_first_answer(DRAMA_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Комедия'):
        db_manager.add_record(username, get_cat1_for_identifier(COMEDY_IDENTIFIER), get_cat2_for_identifier(COMEDY_IDENTIFIER))
        make_first_answer(COMEDY_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Балет'):
        db_manager.add_record(username, get_cat1_for_identifier(BALLET_IDENTIFIER), get_cat2_for_identifier(BALLET_IDENTIFIER))
        make_first_answer(BALLET_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Моноспектакль'):
        db_manager.add_record(username, get_cat1_for_identifier(MONOSPECT_IDENTIFIER), get_cat2_for_identifier(MONOSPECT_IDENTIFIER))
        make_first_answer(MONOSPECT_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Эксперементальный театр'):
        db_manager.add_record(username, get_cat1_for_identifier(EXP_THEATRE_IDENTIFIER), get_cat2_for_identifier(EXP_THEATRE_IDENTIFIER))
        make_first_answer(EXP_THEATRE_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Кукольный спектакль'):
        db_manager.add_record(username, get_cat1_for_identifier(PUPPET_SHOW_IDENTIFIER), get_cat2_for_identifier(PUPPET_SHOW_IDENTIFIER))
        make_first_answer(PUPPET_SHOW_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Фольклор'):
        db_manager.add_record(username, get_cat1_for_identifier(FOLKLORE_IDENTIFIER), get_cat2_for_identifier(FOLKLORE_IDENTIFIER))
        make_first_answer(FOLKLORE_IDENTIFIER, chat_id, process_step_2)

    # this is concert
    elif message.text==('Опера'):
        db_manager.add_record(username, get_cat1_for_identifier(OPERA_IDENTIFIER), get_cat2_for_identifier(OPERA_IDENTIFIER))
        make_first_answer(OPERA_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Классическая музыка'):
        db_manager.add_record(username, get_cat1_for_identifier(CLASSIC_MUSIC_IDENTIFIER), get_cat2_for_identifier(CLASSIC_MUSIC_IDENTIFIER))
        make_first_answer(CLASSIC_MUSIC_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Фольклорная музыка'):
        db_manager.add_record(username, get_cat1_for_identifier(FOLKLORE_MUSIC_IDENTIFIER), get_cat2_for_identifier(FOLKLORE_MUSIC_IDENTIFIER))
        make_first_answer(FOLKLORE_MUSIC_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Джаз'):
        db_manager.add_record(username, get_cat1_for_identifier(JAZZ_IDENTIFIER), get_cat2_for_identifier(JAZZ_IDENTIFIER))
        make_first_answer(JAZZ_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Органная музыка'):
        db_manager.add_record(username, get_cat1_for_identifier(ORGAN_MUSIC_IDENTIFIER), get_cat2_for_identifier(ORGAN_MUSIC_IDENTIFIER))
        make_first_answer(ORGAN_MUSIC_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Авторская песня'):
        db_manager.add_record(username, get_cat1_for_identifier(AUTHOR_SONG_IDENTIFIER), get_cat2_for_identifier(AUTHOR_SONG_IDENTIFIER))
        make_first_answer(AUTHOR_SONG_IDENTIFIER, chat_id, process_step_2)

    # this is exhibition
    elif message.text==('Современное Искусство'):
        db_manager.add_record(username, get_cat1_for_identifier(MODERN_ART_EXHIBIT_IDENTIFIER), get_cat2_for_identifier(MODERN_ART_EXHIBIT_IDENTIFIER))
        make_first_answer(MODERN_ART_EXHIBIT_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Фотография'):
        db_manager.add_record(username, get_cat1_for_identifier(PHOTO_IDENTIFIER), get_cat2_for_identifier(PHOTO_IDENTIFIER))
        make_first_answer(PHOTO_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Графика'):
        db_manager.add_record(username, get_cat1_for_identifier(GRAPHIC_IDENTIFIER), get_cat2_for_identifier(GRAPHIC_IDENTIFIER))
        make_first_answer(GRAPHIC_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Живопись'):
        db_manager.add_record(username, get_cat1_for_identifier(PAINTING_IDENTIFIER), get_cat2_for_identifier(PAINTING_IDENTIFIER))
        make_first_answer(PAINTING_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Дизайн'):
        db_manager.add_record(username, get_cat1_for_identifier(DESIGN_IDENTIFIER), get_cat2_for_identifier(DESIGN_IDENTIFIER))
        make_first_answer(DESIGN_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Скульптура'):
        db_manager.add_record(username, get_cat1_for_identifier(SCULPTURE_IDENTIFIER), get_cat2_for_identifier(SCULPTURE_IDENTIFIER))
        make_first_answer(SCULPTURE_IDENTIFIER, chat_id, process_step_2)
    elif message.text==('Главное меню'):
        start(message)
    else:
        print("Unknown command")


# use that function to make first message
# after that will used @callback_query_handler
def make_first_answer(source_identifier, chat_id, handler):
    print('received source_identifier {}'.format(source_identifier))

    # check limitations
    if not rate_limiter.can_send_to(chat_id):
        update_drop_msg()
        fake_step = FakeMessage(chat_id)
        bot.register_next_step_handler(fake_step, handler)
        return

    # prepare data for source_identifier
    event_url = get_url_for_identifier(source_identifier)
    events_list = get_getter_for_identifier(source_identifier)(event_url)
    if events_list:
        text = get_slicer_for_identifier(source_identifier)(events_list, 0, PAGE_STEP)
        # send data to user
        update_sent_msg()
        next_step = bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown',
                reply_markup=make_inline_buttons(0, PAGE_STEP, len(events_list), source_identifier))
    else:
        text = MIN_CULT_CONNECTION_ERROR
        update_sent_msg()
        next_step = bot.send_message(chat_id=chat_id, text=text)

    rate_limiter.send_to(chat_id)
    bot.register_next_step_handler(next_step, handler)


if __name__ == "__main__":
    initialize()
    db_manager.initialize()
    bot.remove_webhook()
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        print("polling error: {}".format(err))
        time.sleep(RETRY_TIME)
