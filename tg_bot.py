import time

import requests
import telebot
from aiogram.types import ParseMode

from auth_data import token
from parsing_site import *
from aiogram.utils.markdown import hlink, hbold

dict_inst_barbers = {
    'Михаил': {
        'inst': "https://www.instagram.com/mikhail.kulikov_/",
        'inst_name': "mikhail.kulikov_"
        },
    'Искандер': {
        'inst': "https://www.instagram.com/iskander.barber/",
        'inst_name': "iskander.barber"
    },
    'default_inst': {
        'inst': "https://www.instagram.com/blackpapa.kz/",
        'inst_name': "blackpapa.kz"
    },
}

dict_barbers = get_barbers()
current_param = None
record_details = {}

list_bookingdays = []
list_timesbooking = []
dict_services = {}
list_clearmessages = []

def main():

    record_details = {}
    print("Telegram bot working...")
    bot = telebot.TeleBot(token)

    def clear_variables():
        global list_services, list_bookingdays, list_timesbooking, current_param
        dict_services = {}
        list_bookingdays = []
        list_timesbooking = []
        current_param = None

    def clear_messages(chat_id, list_clearmessages):
        for i_del in list_clearmessages:
            bot.delete_message(chat_id, i_del)
        list_clearmessages.clear() #check remove from global list


    #commands
    @bot.message_handler(commands=['start'])
    def start_message(message):
        clear_variables()
        clear_messages(message.chat.id, [message.id])
        inline_markup = telebot.types.InlineKeyboardMarkup()
        record_button = telebot.types.InlineKeyboardButton('Записаться', callback_data='record_begin')
        info_button = telebot.types.InlineKeyboardButton('Инфо', callback_data='info_barber')
        message_id = bot.send_photo(message.chat.id,
                       photo="https://promogorod.kz/uploads/post/43bf81ef60b7a762c339497a9c547eb6.jpg",
                       caption="""BLACK💈PAPA💈BARBERSHOP
✂Стрижем и бреем
Рабочий номер
+7 778 066 13 13
⠀
📍Бекет-Батыра 116
⠀
🕙 С 11:00 до 20:00
⠀
🔒БЕЗ ВЫХОДНЫХ""",
                       reply_markup=inline_markup)
        list_clearmessages.append(message_id)

    #Alisher add main menu
    # @bot.message_handler(commands=['main'])
    bot.message_handler(func=lambda call: call.data == 'record_begin')
    def button_message(message):
        clear_variables()
        list_clearmessages.append(message.id)
        clear_messages(list_clearmessages)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_barber = telebot.types.KeyboardButton("Барберы")
        markup.add(button_barber)
        button_info = telebot.types.KeyboardButton('/info')
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)

    #calls
    @bot.callback_query_handler(func=lambda call: call.data == 'enroll')
    def enroll_record(call):

        list_services_var = [i for i in record_details.get('services').values()]
        list_appointments_var = [{
            'services': list_services_var,
            'staff_id': record_details.get('barber').get('id_barber'),
            'datetime': record_details.get('datetime'),
            'chargeStatus': "",
            'custom_fields': {},
            'id': 0
        }]

        post_variable = {
            'fullname': record_details.get('client_name'),
            'phone': record_details.get('client_phone'),
            'email': record_details.get('client_email', ''),
            'comment': record_details.get('client_comment', ''),
            'appointments': list_appointments_var,
            'bookform_id': 70280,
            'isMobile': False,
            'notify_by_sms': 1,
            'referrer': "https://web.telegram.org/"
        }



        if post_create_record(post_variable):
            bot.send_message(call.message.chat.id, "Вы записаны!")

    @bot.callback_query_handler(func=lambda call: True)
    def callback_bookday(call):
        if call.data in list_bookingdays:
            bot.answer_callback_query(call.id, f"Дата выбрана: {call.data}")
            dict_timesbooking = get_bookingtime(record_details.get('barber').get('id_barber'), call.data)

            inline_markup = telebot.types.InlineKeyboardMarkup()
            for i_booktimes in dict_timesbooking:
                i_datetime = f"{call.data}T{i_booktimes.get('time')}"
                button_booktimes = telebot.types.InlineKeyboardButton(text=i_booktimes.get('time'), callback_data=i_datetime)
                inline_markup.add(button_booktimes)
                list_timesbooking.append(i_datetime)

            bot.send_message(call.message.chat.id, "Выберите время записи:", reply_markup=inline_markup)
        elif call.data in list_timesbooking:

            bot.answer_callback_query(call.id, f"Запись будет установлена на {call.data}")

            record_details['datetime'] = call.data

            list_structure_services = get_bookingservices(record_details.get('barber').get('id_barber'), record_details.get('datetime'))

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for service in list_structure_services:

                if not service.get('active'):
                    continue

                name_service = service.get('title')
                dict_services[name_service] = service.get('id')
                # {
                #     name_service: service.get('id')
                # })

                service_image_url = service.get('image')
                servicce_description = f"Услуга: {name_service}\nЦена: {service.get('price_max')}\nОписание: {service.get('comment')}Длительность: {int(service.get('seance_length') / 60)} минут"

                if service_image_url:
                    bot.send_photo(call.message.chat.id, photo=service_image_url, caption=servicce_description)
                else:
                    bot.send_message(call.message.chat.id, text=servicce_description)

                button_service = telebot.types.KeyboardButton(name_service)
                markup.add(button_service)

            button_done = telebot.types.KeyboardButton('Готово')
            markup.add(button_done)
            bot.send_message(call.message.chat.id, "Выберите услугу", reply_markup=markup)

            global current_param
            current_param = 'services'

    #texts
    @bot.message_handler(func=lambda message: message.text == '78')
    def sun_of_heart(message):
        bot.send_message(message.chat.id, '❤Солнце❤')

    @bot.message_handler(func=lambda message: message.text == "Барберы")
    def barbers(message):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        dict_barbers = get_barbers()
        dict_barbers['Любой'] = {
            'id_barber': -1,
            'name': 'Любой'
        }

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        for name_barber, barber_info in dict_barbers.items():
            if not barber_info.get('avatar'):
                continue
            inst_info = dict_inst_barbers.get(name_barber, None)
            if not inst_info:
                inst_info = dict_inst_barbers.get('default_inst')
            inline_markup = telebot.types.InlineKeyboardMarkup()
            button_inst = telebot.types.InlineKeyboardButton(text=f"inst: {inst_info.get('inst_name')}",
                                                             url=inst_info.get('inst'))
            inline_markup.add(button_inst)
            bot.send_photo(message.chat.id, photo=barber_info.get('avatar'), caption=f"""
                    Имя: {name_barber}\nКатегория: {barber_info.get('specialization')}
                """, reply_markup=inline_markup)

            button_barber = telebot.types.KeyboardButton(name_barber)
            markup.add(button_barber)

        button_anybarber = telebot.types.KeyboardButton('Любой')
        button_back = telebot.types.KeyboardButton('/main')

        markup.add(button_anybarber, button_back)
        bot.send_message(message.chat.id, "Выберите подходящего барбера", reply_markup=markup)

    @bot.message_handler(content_types='text')
    def message_reply(message):

        global current_param

        if message.text in dict_barbers.keys():

            record_details['barber'] = dict_barbers.get(message.text)

            global list_bookingdays
            list_bookingdays = get_bookingday(record_details.get('barber').get('id_barber'))

            inline_markup = telebot.types.InlineKeyboardMarkup()

            for i_days in list_bookingdays:
                button_date = telebot.types.InlineKeyboardButton(text=i_days, callback_data=i_days)
                inline_markup.add(button_date)

            message_id = bot.send_message(message.chat.id, "Выберите дату записи:", reply_markup='').id
            bot.edit_message_text(text="Выберите дату записи:", chat_id=message.chat.id, message_id=message_id, reply_markup=inline_markup)

        elif message.text == 'Готово':

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_mainmenu = telebot.types.KeyboardButton('\main')
            button_recordedit = telebot.types.KeyboardButton('Редактировать запись')

            markup.add(button_mainmenu, button_recordedit)

            bot.send_message(message.chat.id, "Введите номер телефона\n"
                                              "Будет использован для подтверждения записи\n"
                                               "(Пример: +77777777777 или 87777777777)")
            current_param = 'phone'

        elif current_param == 'phone':
            if not ((message.text[0:3] == '+77' and len(message.text) == 12) or (message.text[0:2] == '87' and len(message.text) == 11)):
                bot.send_message(message.chat.id, "Неверный формат номера телефона!\n"
                                                    "(Пример: +77777777777 или 87777777777)")
                return

            record_details['client_phone'] = message.text
            bot.send_message(message.chat.id, "Введите ваше имя:")

            current_param = 'client_name'

        elif current_param == 'client_name':
            if len(message.text) < 3:
                bot.send_message(message.chat.id, "Имя должно содержать более 3 символов")
                return

            record_details['client_name'] = message.text

            current_param = None

            inline_markup = telebot.types.InlineKeyboardMarkup()

            text_recorddetails = f"""
                                    Ваша запись:
                                        Гость: {record_details.get('client_name')}
                                        Телефон: {record_details.get('client_phone')}    
                                        Электронная почта: {record_details.get('client_email', '')}
                                        Комментарии к записи: {record_details.get('client_comment', '')}
                                        Барбер: {record_details.get('barber').get('name')}
                                        Дата/время записи: {record_details.get('datetime')}
                                        Услуги: """

            dict_choosen_services = record_details.get('services', {})

            if dict_choosen_services:
                for i_chservices in dict_choosen_services.keys():
                    text_recorddetails += '\n' + i_chservices
            else:
                text_recorddetails += 'Нет услуг'

            inline_markup = telebot.types.InlineKeyboardMarkup()
            button_enroll = telebot.types.InlineKeyboardButton(text='Записаться', callback_data='enroll')
            inline_markup.add(button_enroll)

            bot.send_message(message.chat.id, text_recorddetails, reply_markup=inline_markup)

        elif current_param == 'services':

            dict_choosen_services = record_details.get('services', {})

            if message.text not in dict_services.keys():
                bot.send_message(message.chat.id, "Некорректная услуга!")
                return

            if message.text in dict_choosen_services.keys():
                bot.send_message(message.chat.id, "Данная услуга уже была добавлена")
                return

            dict_choosen_services[message.text] = dict_services.get(message.text)
            bot.send_message(message.chat.id, f"{message.text} добавлен(а) в список услуг.")
            record_details['services'] = dict_choosen_services






    # bot.polling(none_stop=True, timeout=30)
    try:
        bot.infinity_polling(timeout=10)
    except:
        time.sleep(15)




if __name__ == '__main__':
    main()