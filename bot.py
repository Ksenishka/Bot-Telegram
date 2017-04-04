# -*- coding: utf-8 -*- 

import telebot
from telebot import types
import json
from urllib.request import urlopen
import requests
import urllib.request
import urllib.parse

bot = telebot.TeleBot("325597084:AAF4cA-uCDYjmd7m0-pSaIxwyD7kjH7MLlg")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Выставки \U0001F3A8', 'Спектакли \U0001F3AD', 'Концерты \U0001F3BC', 'Кинопоказ \U0001F4FA', 'Лекции \U0001F4DA') 
    next_step = bot.send_message(message.chat.id, 'Выберете интересующее вас направление.', reply_markup=markup)
    bot.register_next_step_handler(next_step, process_step)
    username = str(message.chat.username)
    #send_stat = urllib.request.urlopen("http://admin.theartr.ru/stat_backend/user?username="+username + '&action=connected')

    #print (username)

    # GET запрос
    #data = {"username": username, 'action': 'connected'}
    #enc_data = urllib.parse.urlencode(data)
    #url_connection = urllib.request.urlopen("http://admin.theartr.ru/stat_backend/user" + "?" + enc_data)
    #print(url_connection.read())



# Globally defined types
PAGE_STEP = 3
FILMS_IDENTIFIER = 4
LECTURES_IDENTIFIER = 5

def get_list_of_films():
    resp = urlopen("https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&tags=164").read().decode('utf8')
    events = json.loads(resp)
    events_films = []
    for event in events['events']:
        events_films.append({'name': event['name'], 'place': event['places'][0]['name'], 'address': event['places'][0]['address'],
            'price': event['price'], "shortDescription": event["shortDescription"], "url": event["externalInfo"][0]['url']})
    return events_films

def get_slice_of_films(events_films, start, stop):
    result = ''
    for event in events_films[start : stop]:
        if('name' in event):
            name = '*' + event['name'] + '*' + '\n\n'
        else:
            name = ''

        if('name' in event['place']):
            place = 'Место проведения: ' + event['place'] + '\n\n'
        else:
            place = ''

        if('source' in event['address']):
            address = 'Адрес: ' + event['address']['source'] + '\n\n'
        else:
            address = ''

        if("shortDescription" in event):
            short_desc = 'Краткое описание: ' + event['shortDescription'] + '\n\n'
        else:
            short_desc = ''
        if('url' in event):
            show_url = 'Подробнее: ' + event['url'] + '\n\n'
        else:
            show_url = ''

        result += name + place + address + short_desc + show_url + '\n\n'
    return result

def get_list_of_lectures():
        resp = urlopen("https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&&tags=102").read().decode('utf8')
        events = json.loads(resp)
        events_lectures = []
        for event in events['events']:
            events_lectures.append({'name': event['name'], 'place': event['places'][0]['name'], 'address': event['places'][0]['address'], 
                'price': event['price'], "shortDescription": event["shortDescription"], "url": event["externalInfo"][0]['url']})  
        return events_lectures

def get_slice_of_lectures(events_lectures, start, stop):        
    result = ''
    for event in events_lectures[start : stop]:
        if('name' in event):
            name = '*' + event['name'] + '*' + '\n\n'
        else:
            name = ''

        if('name' in event['place']):
            place = 'Место проведения: ' + event['place'] + '\n\n'
        else:
            place = ''

        if('source' in event['address']):
            address = 'Адрес: ' + event['address']['source'] + '\n\n'
        else:
            address = ''

        if("shortDescription" in event):
            short_desc = 'Краткое описание: ' + event['shortDescription'] + '\n\n'
        else:
            short_desc = ''
        if('url' in event):
            show_url = 'Подробнее: ' + event['url'] + '\n\n'
        else:
            show_url = ''

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
        print("Something wrong")
        return

    source_identifier = int(parts[0])
    offset = int(parts[1])

    if source_identifier == FILMS_IDENTIFIER:
        events_list = get_list_of_films()
        text = get_slice_of_films(events_list, offset, offset + PAGE_STEP)
        bot.edit_message_text(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            text = text,
            parse_mode = 'Markdown',
            reply_markup = make_inline_buttons(offset, offset + PAGE_STEP, len(events_list), FILMS_IDENTIFIER))

    elif source_identifier == LECTURES_IDENTIFIER:
        events_list = get_list_of_lectures()
        text = get_slice_of_films(events_list, offset, offset + PAGE_STEP)
        bot.edit_message_text(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            text = text,
            parse_mode = 'Markdown',
            reply_markup = make_inline_buttons(offset, offset + PAGE_STEP, len(events_list), LECTURES_IDENTIFIER))
    else:
        print("Unknown source identifier (maybe didn't implemented)")


def process_step(message):
    chat_id = message.chat.id
    if message.text=='Спектакли \U0001F3AD':
        print('Performances')

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

        next_step = bot.send_message(message.chat.id,'Какое направление предпочитаете? \nДля полного списка прокрутите вниз!', reply_markup=markup)
        bot.register_next_step_handler(next_step, process_step_2) 

    elif message.text==('Кинопоказ \U0001F4FA'):
        #url_cat2 = urllib.request.urlopen('http://admin.theartr.ru/stat_backend/click?cat1=Film_screening&username=' + message.chat.username)
        print('Film screening')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item =  types.KeyboardButton('Главное меню')
        markup.row(item) 

        events_list = get_list_of_films()
        text = get_slice_of_films(events_list, 0, PAGE_STEP)
        next_step = bot.send_message(message.chat.id, text, reply_markup=markup, reply_markup=make_inline_buttons(0, PAGE_STEP, len(events_list), FILMS_IDENTIFIER), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 

    elif message.text==('Лекции \U0001F4DA'):
        #url_cat2 = urllib.request.urlopen('http://admin.theartr.ru/stat_backend/click?cat1=Lectures&username=' + message.chat.username)
        print('Lectures')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item =  types.KeyboardButton('Главное меню')
        markup.row(item) 

        events_list = get_list_of_lectures()
        text = get_slice_of_lectures(events_list, 0, PAGE_STEP)
        next_step = bot.send_message(message.chat.id, text, reply_markup=markup, reply_markup=make_inline_buttons(0, PAGE_STEP, len(events_list), LECTURES_IDENTIFIER), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 

        #next_step = bot.send_message(message.chat.id, result, reply_markup=markup, parse_mode='Markdown')
        

    elif message.text=='Концерты \U0001F3BC':
        print('Concerts')

        url_cat2 = urllib.request.urlopen('http://admin.theartr.ru/stat_backend/click?cat1=Concerts&username=' + message.chat.username)

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

        next_step = bot.send_message(message.chat.id, 'Какое направление предпочитаете? \nДля полного списка прокрутите вниз!', reply_markup=markup)
        bot.register_next_step_handler(next_step, process_step_2) 

    elif message.text=='Выставки \U0001F3A8':
        print('Exhibitions')

        url_cat2 = urllib.request.urlopen('http://admin.theartr.ru/stat_backend/click?cat1=Exhibitions&username=' + message.chat.username)

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

        next_step = bot.send_message(message.chat.id, 'Какое направление предпочитаете? \n Для полного списка прокрутите вниз!', reply_markup=markup)
        bot.register_next_step_handler(next_step, process_step_2) 



def process_step_2(message):
    chat_id = message.chat.id
    if message.text==("Трагикомедия"):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Tragic", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=9", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)
    elif message.text==("Современное искусство"):
        next_step = bot.send_message(message.chat.id, create_response("Performances","Modern_art", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=26", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)
    elif message.text==('Классическое искусство'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Classical_art", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=25", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)
    elif message.text==('Драма'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Drama", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=267", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)
    elif message.text==('Комедия'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Comedy", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=266", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Балет'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Ballet", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=31", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Моноспектакль'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Monospect", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=260", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)   
    elif message.text==('Эксперементальный театр'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Experimental_theatre", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=97", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Кукольный спектакль'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Puppet_show", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=184", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Фольклор'):
        next_step = bot.send_message(message.chat.id, create_response("Performances", "Folklore", "https://all.culture.ru/api/2.2/events?status=accepted&locales=2579&categories=spektakli&tags=208", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Опера'):
        next_step = bot.send_message(message.chat.id, create_response("Concerts", "Opera", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=koncerty&tags=30", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Классическая музыка'):
        next_step = bot.send_message(message.chat.id, create_response("Concerts", "Classical_music", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=koncerty&tags=158", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Фольклорная музыка'):
        next_step = bot.send_message(message.chat.id, create_response("Concerts", "Folklore_music", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=koncerty&tags=208", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Джаз'):
        next_step = bot.send_message(message.chat.id, create_response("Concerts", "Jazz", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=koncerty&tags=155", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Органная музыка'):
        next_step = bot.send_message(message.chat.id, create_response("Concerts", "Organ_music", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=koncerty&tags=157", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)
    elif message.text==('Авторская песня'):
        next_step = bot.send_message(message.chat.id, create_response("Concerts", "Author_song", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=koncerty&tags=181", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)
    elif message.text==('Современное Искусство'):
        next_step = bot.send_message(message.chat.id, create_response("Exhibitions", "Modern_art_exhibit", 'https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=vystavki&tags=26', message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Фотография'):
        next_step = bot.send_message(message.chat.id, create_response("Exhibitions", "Photo", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=vystavki&tags=50", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)  
    elif message.text==('Графика'):
        next_step = bot.send_message(message.chat.id, create_response("Exhibitions", "Graphic", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=vystavki&tags=160", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2)  
    elif message.text==('Живопись'):
        next_step = bot.send_message(message.chat.id, create_response("Exhibitions", "Painting", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=vystavki&tags=163", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Дизайн'):
        next_step = bot.send_message(message.chat.id, create_response("Exhibitions", "Design", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=vystavki&tags=48", message), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Скульптура'):
        next_step = bot.send_message(message.chat.id, create_response("Exhibitions", "Sculpture", "https://all.culture.ru/api/2.2/events?status=accepted&start=1488821641399&locales=2579&categories=vystavki&tags=91"), parse_mode='Markdown')
        bot.register_next_step_handler(next_step, process_step_2) 
    elif message.text==('Главное меню'):
        start(message)
    else:
        print("Unknown command")

def check_server(url):
    try:
        r = requests.head(url)
        statusCode = r.status_code
    except requests.ConnectionError:
        print("Failed to connect server")

    if(statusCode == 200):
        resp = urlopen(url).read().decode('utf8')
        result = [resp, statusCode]

    else:
        resp = 'Не удалось соедениться с сервером МинКульт'
        result = [resp, statusCode]

    return result

def create_response(resp_cat1, resp_cat2, url, message):
    resp = check_server(url)
    if(resp[1] == 200):
        events = json.loads(resp[0])
        spisok_sobitiy = []
        for event in events['events']:
               spisok_sobitiy.append({'name': event['name'], 'place': event['places'], 'address': event['places'][0]['address'], 
                  'price': event['price'], "shortDescription": event["shortDescription"], "url": event["externalInfo"][0]['url']})  
        result = ''
        for eventik in spisok_sobitiy[:5]:
            if('name' in eventik):
                name = '*' + eventik['name'] + '*' + '\n\n'
            else:
                name = ''

            if('name' in eventik['place']):
                place = 'Место проведения: ' + eventik['place'] + '\n\n'
            else:
                place = ''

            if('source' in eventik['address']):
                address = 'Адрес: ' + eventik['address']['source'] + '\n\n'
            else:
                address = ''

            if("shortDescription" in eventik):
                short_desc = 'Краткое описание: ' + eventik['shortDescription'] + '\n\n'
            else:
                short_desc = ''
            if('url' in eventik):
                show_url = 'Подробнее: ' + eventik['url'] + '\n\n'
            else:
                show_url = ''

            result += name + place + address + short_desc + show_url + '\n\n'


    else:
        result = resp[0]

    username = str(message.chat.username)
    data = {'cat1': resp_cat1, 'cat2': resp_cat2, "username": username}
    #url_cat2 = urllib.request.urlopen("http://admin.theartr.ru/stat_backend/click?cat1=" + resp_cat1 + '&cat2=' + resp_cat2 + '&username=' + username)
    # TODO
    return


if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling()