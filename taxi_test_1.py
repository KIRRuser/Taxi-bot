import telebot
from telebot import types
import sqlite3
from datetime import datetime, date
import config_taxibot

connect = sqlite3.connect('TAXIdata.db')
cursor = connect.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS making_orders
             (id INTEGER PRIMARY KEY,
              username TEXT,
              first_name TEXT,
              last_name TEXT,
              phone_number TEXT,
              message_id INTEGER,
              user_adress TEXT,
              message TEXT,
              end_adress TEXT,
              sale TEXT,
              del_msg_id INTEGER,
              del_msg_id2 INTEGER,
              msg_id_order INTEGER,
              driver_msg_id_order INTEGER,
              who_accept TEXT,
              ordermid INTEGER,
              permissions TEXT,
              key TEXT,
              date TEXT,
              time1 TEXT,
              time2 TEXT,
              page TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS drivers
             (id INTEGER PRIMARY KEY,
              status TEXT,
              order_status TEXT,
              username TEXT,
              phone_number TEXT,
              fio TEXT,
              car TEXT,
              state_number TEXT,
              trips INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS orders
             (order_number INTEGER PRIMARY KEY AUTOINCREMENT,
              customer_phone TEXT,
              driver TEXT,
              date TEXT,
              time TEXT,
              user_adress TEXT,
              end_adress TEXT,
              sale TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS configuration
             (id_group INTEGER PRIMARY KEY)''')

connect.commit()
connect.close()


class Bot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.id_group = config_taxibot.id_group
        self.btn_cancel = types.InlineKeyboardButton(
            text='Отменить заказ ❌',
            callback_data='main'
        )

    def start(self):

        @self.bot.message_handler(commands=['start'])
        def command_start(message):
            if message.from_user.username is None:
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_how = types.InlineKeyboardButton(text='Как указать?',
                                                     callback_data='how'
                                                     )
                keyboard.add(btn_how)
                self.bot.send_message(chat_id=message.chat.id,
                                      text=f'ℹ️ {message.from_user.first_name}, для корректной работы сервиса у вас ОБЯЗАТЕЛЬНО должно'
                                           f'быть указано имя пользователя!',
                                      reply_markup=keyboard
                                      )
            else:
                try:
                    keyboard = types.ReplyKeyboardMarkup(row_width=1,
                                                         resize_keyboard=True,
                                                         one_time_keyboard=True
                                                         )
                    btn_number = types.KeyboardButton(text='Подтвердить номер телефона 📲',
                                                      request_contact=True
                                                      )
                    keyboard.add(btn_number)
                    self.bot.send_message(chat_id=message.chat.id,
                                          text=f'ℹ️ {message.from_user.first_name}, Вас приветствует бот диспетчер такси! '
                                               f'для продолжения использования подтвердите номер телефона.',
                                          reply_markup=keyboard
                                          )
                    self.bot.register_next_step_handler(message, contact)
                except:
                    pass

        # @self.bot.message_handler(commands=['remove'])
        # def handle_contact(message):
        #     self.bot.send_message(message.chat.id, 'Кнопка удалена.', reply_markup=types.ReplyKeyboardRemove())

        @self.bot.message_handler(content_types=['contact'])
        def contact(message):
            if message.from_user.username is None:
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_how = types.InlineKeyboardButton(text='Как указать?',
                                                     callback_data='how'
                                                     )
                keyboard.add(btn_how)
                self.bot.send_message(chat_id=message.chat.id,
                                      text=f'ℹ️ {message.from_user.first_name}, для корректной работы сервиса у вас ОБЯЗАТЕЛЬНО должно'
                                           f'быть указано имя пользователя!',
                                      reply_markup=keyboard
                                      )
            else:
                try:
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    btn_main = types.InlineKeyboardButton(text='Начать ▶️',
                                                          callback_data='main'
                                                          )
                    keyboard.add(btn_main)

                    # now = datetime.now()
                    # current_time = now.strftime("%H:%M:%S")
                    #
                    # current_date = date.today()
                    conn = sqlite3.connect('TAXIdata.db')
                    cursor = conn.cursor()
                    cursor.execute(f'SELECT id FROM making_orders WHERE id = {message.contact.user_id}')
                    data = cursor.fetchone()
                    if data is None:
                        self.bot.send_message(chat_id=message.chat.id,
                                              text='Номер телефона успешно подтвержден ✅',
                                              reply_markup=types.ReplyKeyboardRemove(),
                                              )
                        self.bot.send_message(chat_id=message.chat.id,
                                              text='Начинаем работу?',
                                              reply_markup=keyboard
                                              )
                        cursor.execute('''INSERT INTO making_orders 
                                                (id, 
                                                username, 
                                                first_name, 
                                                last_name, 
                                                phone_number)
                                                VALUES (?, ?, ?, ?, ?)''',
                                       (
                                           message.contact.user_id,
                                           message.from_user.username,
                                           message.contact.first_name,
                                           message.contact.last_name,
                                           message.contact.phone_number)
                                       )
                        conn.commit()
                        conn.close()
                    else:
                        self.bot.send_message(chat_id=message.chat.id,
                                              text=f'ℹ️ {message.from_user.first_name}, Ваш номер телефона уже подтвержден.',
                                              reply_markup=types.ReplyKeyboardRemove()
                                              )
                        self.bot.send_message(chat_id=message.chat.id,
                                              text='Начинаем работу?',
                                              reply_markup=keyboard
                                              )
                except:
                    pass

        @self.bot.callback_query_handler(func=lambda callback: callback.data)
        def check_callback(callback):

            """Пользовательская часть"""
            if callback.data == 'how':
                self.bot.send_message(chat_id=callback.message.chat.id,
                                      text='Для указания имени пользователя следуйте следующим шагам:'
                                           '\nВ телеграмм откройте "Настройки"'
                                           '\nОколо вашего профиля нажмите на "Изменить"'
                                           '\nПридумайте и укажите имя пользователя'
                                      )

            if callback.data == 'main':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"SELECT driver_msg_id_order FROM making_orders WHERE id = {callback.message.chat.id}")
                dmid = cursor.fetchone()
                if dmid[0] is None:
                    pass
                else:
                    cursor.execute(f"SELECT id_group FROM configuration")
                    gid = cursor.fetchone()
                    if gid[0] is None:
                        pass
                    else:
                        cursor.execute(f"SELECT who_accept FROM making_orders WHERE id = ?",
                                       (callback.message.chat.id,))
                        cmi = cursor.fetchone()
                        if cmi[0] is None:
                            try:
                                self.bot.edit_message_text(chat_id=gid[0],
                                                           message_id=dmid[0],
                                                           text='Закан отменен.'
                                                           )
                            except:
                                pass
                        else:
                            pass
                        try:
                            self.bot.delete_message(chat_id=gid[0],
                                                    message_id=dmid[0] + 1
                                                    )
                            self.bot.delete_message(chat_id=gid[0],
                                                    message_id=dmid[0] + 2
                                                    )
                        except:
                            pass
                cursor.execute(
                    f"UPDATE making_orders SET "
                    f"message_id = NULL,"
                    f"user_adress = NULL,"
                    f"message = NULL,"
                    f"sale = NULL,"
                    f"del_msg_id = NULL,"
                    f"del_msg_id2 = NULL,"
                    f"msg_id_order = NULL,"
                    f"driver_msg_id_order = NULL,"
                    f"who_accept = NULL,"
                    f"ordermid = NULL,"
                    f"date = NULL,"
                    f"time1 = NULL,"
                    f"time2 = NULL,"
                    f"page = NULL,"
                    f"end_adress = NULL WHERE id = {callback.message.chat.id}"
                )
                keyboard = types.InlineKeyboardMarkup()
                btn_order = types.InlineKeyboardButton(text='Заказать машину 🚕',
                                                       callback_data='order'
                                                       )
                keyboard.add(btn_order)
                cursor.execute(f"SELECT status FROM drivers")
                data = cursor.fetchall()
                drivers = 0
                for i in range(len(data)):
                    drivers += data[i][0]
                if drivers >= 1:
                    sms = f'Водителей на смене: {drivers}👤.'
                else:
                    sms = f'На данный момент на смене никого нет.'

                cursor.execute(f"SELECT order_status FROM drivers")
                work_drivers = cursor.fetchall()
                wd = 0
                for i in range(len(work_drivers)):
                    wd += work_drivers[i][0]
                if wd >= 1:
                    sms2 = f'Свободно водителей: {wd}.'
                else:
                    sms2 = f'Все водители заняты.'

                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'{callback.from_user.first_name}, \n{sms}\n{sms2}',
                                           reply_markup=keyboard
                                           )
                conn.commit()
                conn.close()

            if callback.data == 'order':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute("SELECT "
                               "user_adress,"
                               "end_adress,"
                               "message,"
                               "message_id,"
                               "sale"
                               " FROM making_orders WHERE id = ?", (callback.message.chat.id,)
                               )

                result = cursor.fetchone()

                if result[0] is None:
                    line_user_adress = 'Не указан'
                else:
                    if result[3] is None:
                        line_user_adress = result[0]
                    else:
                        line_user_adress = 'Указан на карте'

                if result[1] is None:
                    line_end_adress = 'Не указан'
                else:
                    line_end_adress = result[1]

                if result[2] is None:
                    line_message_for_driver = 'Не указано'
                else:
                    line_message_for_driver = result[2]

                if result[4] is None:
                    line_sale = 'Стандартная по городу - 100р'
                else:
                    line_sale = result[4]
                keyboard = types.InlineKeyboardMarkup(row_width=1)

                btn_give_user_adress = types.InlineKeyboardButton(text='Изменить текущий адрес 🏠',
                                                                  callback_data='give_user_adress'
                                                                  )
                btn_give_end_adress = types.InlineKeyboardButton(text='Изменить конечный адрес 🏡',
                                                                 callback_data='give_end_adress'
                                                                 )
                # btn_child_seat = types.InlineKeyboardButton(text='Необходимо детское кресло',
                #                                             callback_data='child_seat'
                #                                             )
                btn_sale = types.InlineKeyboardButton(text='Предложить стоимость поездки 💵',
                                                      callback_data='give_sale')
                btn_message_for_driver = types.InlineKeyboardButton(text='Сообщения для водителя ✉️',
                                                                    callback_data='message_for_driver'
                                                                    )
                btn_order_ready = types.InlineKeyboardButton(text='Заказ готов ✅',
                                                             callback_data='order_is_ready'
                                                             )
                btn_admin_menu = types.InlineKeyboardButton(text='Отчет о поездках 📄',
                                                            callback_data='otchet'
                                                            )
                if result[0] is None:
                    keyboard.add(btn_give_user_adress,
                                 btn_give_end_adress,
                                 btn_sale,
                                 btn_message_for_driver,
                                 self.btn_cancel
                                 )
                else:
                    if result[1] is None:
                        keyboard.add(btn_give_user_adress,
                                     btn_give_end_adress,
                                     btn_sale,
                                     btn_message_for_driver,
                                     self.btn_cancel
                                     )
                    else:
                        keyboard.add(btn_give_user_adress,
                                     btn_give_end_adress,
                                     btn_sale,
                                     btn_message_for_driver,
                                     btn_order_ready,
                                     self.btn_cancel
                                     )
                cursor.execute(f"SELECT permissions FROM making_orders WHERE id = ?",
                               (callback.message.chat.id,))
                admin = cursor.fetchone()
                if admin[0] is None:
                    pass
                else:
                    keyboard.add(btn_admin_menu)
                try:
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text=f'{callback.from_user.first_name}, Вы находитесь в меню оформления заказа.:'
                                                    f'\n🏠 Ваш адрес: {line_user_adress}'
                                                    f'\n🏡 Конечный адрес: {line_end_adress}'
                                                    f'\n💵 Стоимость поездки: {line_sale}'
                                                    f'\n✉️ Сообщение для водителя: {line_message_for_driver}'
                                                    f'\nПо необходимости можете оставить сообщение для водителя.',
                                               reply_markup=keyboard
                                               )
                except:
                    pass
                conn.commit()
                conn.close()

            if callback.data == 'give_user_adress':
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_auto = types.InlineKeyboardButton(text='Автоматически',
                                                      callback_data='auto'
                                                      )
                btn_manually = types.InlineKeyboardButton(text='Вручную',
                                                          callback_data='manually'
                                                          )
                keyboard.add(btn_auto,
                             btn_manually,
                             )
                del_msg_0 = self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                       message_id=callback.message.id,
                                                       text=f'ℹ️ {callback.from_user.first_name}, выберите способ указания вашего адреса',
                                                       reply_markup=keyboard
                                                       )
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE making_orders SET del_msg_id2 = {del_msg_0.message_id} WHERE id = {callback.message.chat.id}")
                conn.commit()
                conn.close()

            if callback.data == 'auto':
                keyboard1 = types.ReplyKeyboardMarkup(row_width=1,
                                                      resize_keyboard=True,
                                                      one_time_keyboard=True
                                                      )

                btn_geo = types.KeyboardButton(text='Отправить адрес',
                                               request_location=True,
                                               )
                keyboard1.add(btn_geo)
                del_msg_1 = self.bot.send_message(chat_id=callback.message.chat.id,
                                                  text=f'{callback.from_user.first_name}, нажмите на кнопку ниже. Если не получается поделиться геолокацией нажмите "Вручную"',
                                                  reply_markup=keyboard1
                                                  )
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE making_orders SET del_msg_id = {del_msg_1.message_id} WHERE id = {callback.message.chat.id}")
                conn.commit()
                conn.close()

            if callback.data == 'manually':
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        f"SELECT del_msg_id FROM making_orders WHERE id = {callback.message.chat.id}")
                    delmsg2 = cursor.fetchone()
                    if delmsg2[0] is None:
                        pass
                    else:
                        self.bot.delete_message(chat_id=callback.message.chat.id,
                                                message_id=delmsg2[0]
                                                )
                except:
                    pass
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_cancel = types.InlineKeyboardButton(text='Отмена',
                                                        callback_data='order')
                keyboard.add(btn_cancel)
                del_msg_2 = self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                       message_id=callback.message.id,
                                                       text=f'ℹ️ {callback.from_user.first_name}, укажите адрес, куда должен подъехать водитель',
                                                       reply_markup=keyboard
                                                       )
                cursor.execute(
                    f"UPDATE making_orders SET del_msg_id = {del_msg_2.message_id} WHERE id = {callback.message.chat.id}")
                conn.commit()
                conn.close()

                self.bot.register_next_step_handler(callback.message, get_user_adress_manually)

            if callback.data == 'give_end_adress':
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_cancel = types.InlineKeyboardButton(text='Отмена',
                                                        callback_data='order'
                                                        )

                keyboard.add(btn_cancel)

                del_msg_3 = self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                       message_id=callback.message.id,
                                                       text=f'ℹ️ {callback.from_user.first_name}, укажите конечный адрес поездки',
                                                       reply_markup=keyboard
                                                       )
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE making_orders SET del_msg_id = {del_msg_3.message_id} WHERE id = {callback.message.chat.id}")
                conn.commit()
                conn.close()

                self.bot.register_next_step_handler(callback.message, get_end_adress)

            if callback.data == 'give_sale':
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_give_sale = types.InlineKeyboardButton(text='Указать стоимость 💵',
                                                           callback_data='user_give_sale'
                                                           )
                btn_no_give_sale = types.InlineKeyboardButton(text='Оставить текущую (100р.) ❌',
                                                              callback_data='order'
                                                              )
                keyboard.add(btn_give_sale,
                             btn_no_give_sale
                             )
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name},'
                                                f'стоимость поездки в пределах города по умолчанию составляет 100р.'
                                                f'Если срочно нужна машина, укажите стоимость больше.'
                                                f'Стоимость поездки за пределы города договаривается с водителем.',
                                           reply_markup=keyboard
                                           )

            if callback.data == 'message_for_driver':
                keyboard = types.InlineKeyboardMarkup()
                btn_cancel = types.InlineKeyboardButton(text='Отмена ❌',
                                                        callback_data='order'
                                                        )
                keyboard.add(btn_cancel)
                del_msg_4 = self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                       message_id=callback.message.id,
                                                       text=f'ℹ️ {callback.from_user.first_name}, введите сообщение для водителя',
                                                       reply_markup=keyboard
                                                       )
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE making_orders SET del_msg_id = {del_msg_4.message_id} WHERE id = {callback.message.chat.id}")
                conn.commit()
                conn.close()

                self.bot.register_next_step_handler(callback.message, message_for_driver)

            if callback.data == 'user_give_sale':
                keyboard = types.InlineKeyboardMarkup()
                btn_cancel = types.InlineKeyboardButton(text='Отмена ❌',
                                                        callback_data='order'
                                                        )
                keyboard.add(btn_cancel)
                del_msg_5 = self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                       message_id=callback.message.id,
                                                       text=f'ℹ️ {callback.from_user.first_name}, укажите стоимость',
                                                       reply_markup=keyboard
                                                       )
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE making_orders SET del_msg_id = {del_msg_5.message_id} WHERE id = {callback.message.chat.id}")
                conn.commit()
                conn.close()

                self.bot.register_next_step_handler(callback.message, give_user_sale)

            if callback.data == 'order_is_ready':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute("SELECT "
                               "user_adress,"
                               "end_adress,"
                               "message,"
                               "message_id,"
                               "sale"
                               " FROM making_orders WHERE id = ?", (callback.message.chat.id,))
                result = cursor.fetchone()
                conn.close()

                if result[3] is None:
                    line_u_a = result[0]
                else:
                    line_u_a = 'Указан на карте'

                if result[2] is None:
                    line_m_f_d = 'Не указано'
                else:
                    line_m_f_d = result[2]

                if result[4] is None:
                    line_s = 'Стандартная - 100р'
                else:
                    line_s = result[4]

                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_right = types.InlineKeyboardButton(text='Верно, оформить заказ ✅',
                                                       callback_data='get_order'
                                                       )
                btn_back = types.InlineKeyboardButton(text='Изменить данные ✏️',
                                                      callback_data='order'
                                                      )
                keyboard.add(btn_right,
                             btn_back,
                             self.btn_cancel
                             )
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ Проверьте правильность данных ‼️'
                                                f'\n🏠 Ваш адрес: {line_u_a}'
                                                f'\n🏡 Конечный адрес: {result[1]}'
                                                f'\n💵 Стоимость поездки: {line_s}'
                                                f'\n✉️ Сообщение для водителя: {line_m_f_d}',
                                           reply_markup=keyboard
                                           )

            if callback.data == 'get_order':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"UPDATE making_orders SET username = ? WHERE id = ?",
                               (callback.from_user.username, callback.message.chat.id))
                conn.commit()
                cursor.execute("SELECT "
                               "user_adress,"
                               "end_adress,"
                               "message,"
                               "message_id,"
                               "sale,"
                               "first_name,"
                               "phone_number,"
                               "msg_id_order,"
                               "username"
                               " FROM making_orders WHERE id = ?", (callback.message.chat.id,))
                result = cursor.fetchone()
                cursor.execute("SELECT id_group FROM configuration")
                id_group = cursor.fetchone()

                if result[3] is None:
                    line_user_adr = result[0]
                else:
                    line_user_adr = 'Указан на карте'
                if result[4] is None:
                    line_sal = 'Стандартная - 100р'
                else:
                    line_sal = result[4]
                if result[2] is None:
                    line_mfd = 'Не указано'
                else:
                    line_mfd = result[2]

                if result[7] is None:

                    keyboard = types.InlineKeyboardMarkup()
                    btn_cancel_order = types.InlineKeyboardButton(text='Отменить заказ ❌',
                                                                  callback_data='really_cancel'
                                                                  )
                    keyboard.add(btn_cancel_order)

                    order_id = self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                          message_id=callback.message.id,
                                                          text=f'ℹ️ {callback.from_user.first_name}, Ваш заказ успешно оформлен! Ожидайте, пока его примут.'
                                                               f'\n🏠 Ваш адрес: {line_user_adr}'
                                                               f'\n🏡 Конечный адрес: {result[1]}'
                                                               f'\n💵 Стоимость поездки: {line_sal}'
                                                               f'\n✉️ Сообщение для водителя: {line_mfd}',
                                                          reply_markup=keyboard
                                                          )
                    cursor.execute(f"UPDATE making_orders SET msg_id_order = ? WHERE id = ?",
                                   (order_id.message_id, callback.message.chat.id,))

                    driver_keyboard = types.InlineKeyboardMarkup()
                    driver_btn_accept_order = types.InlineKeyboardButton(text='Принять заказ',
                                                                         callback_data='driver_accept'
                                                                         )
                    driver_btn_conn = types.InlineKeyboardButton(text='Связь к заказчиком',
                                                                 url=f't.me/{result[8]}')
                    cursor.execute(f"SELECT username FROM making_orders WHERE id = ?",
                                   (callback.message.chat.id,))
                    uiid = cursor.fetchone()
                    # driver_btn_conn = types.InlineKeyboardButton(text='Связь с клиентом', url=f'https://t.me/{uiid[0]}'),

                    driver_keyboard.add(driver_btn_accept_order,
                                        driver_btn_conn
                                        )

                    driver_order_id = self.bot.send_message(chat_id=id_group[0],
                                                            text=f'Заказчик: {result[5]},'
                                                                 f'\nНомер телефона заказчика: {result[6]},'
                                                                 f'\nАдрес заказчика: {line_user_adr},'
                                                                 f'\nКонечный адрес поездки: {result[1]},'
                                                                 f'\nПредложенная стоимость поездки: {line_sal},'
                                                                 f'\nСообщение от заказчика: {line_mfd}',
                                                            reply_markup=driver_keyboard
                                                            )
                    cursor.execute(
                        f"UPDATE making_orders SET driver_msg_id_order = '{driver_order_id.message_id}' WHERE id = {callback.message.chat.id}")
                    conn.commit()
                    conn.close()
                    if result[3] is None:
                        pass
                    else:
                        self.bot.forward_message(chat_id=id_group[0],
                                                 from_chat_id=callback.message.chat.id,
                                                 message_id=result[3],
                                                 )
                        self.bot.send_message(chat_id=id_group[0],
                                              text=f'Адрес заказчика {result[5]} на карте.'
                                              )
                # else:
                #     keyboard = types.InlineKeyboardMarkup()
                #     keyboard.add(self.btn_cancel)
                #     self.bot.edit_message_text(chat_id=callback.message.chat.id,
                #                                message_id=callback.message.id,
                #                                text=f'ℹ️ {callback.from_user.first_name}, У вас уже есть активный заказ! Отменить?',
                #                                reply_markup=keyboard
                #                                )

            if callback.data == 'really_cancel':
                keyboard = types.InlineKeyboardMarkup()

                btn_no_cancel = types.InlineKeyboardButton(text='Не отменять ✅',
                                                           callback_data='get_order')

                btn_really_cancel = types.InlineKeyboardButton(text='Отменить ❌',
                                                               callback_data='main'
                                                               )
                keyboard.add(btn_no_cancel,
                             btn_really_cancel
                             )
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, Вы уверены, что хотите отменить заказ?',
                                           reply_markup=keyboard
                                           )

            """Водительская часть"""

            if callback.data == 'driver_accept' or callback.data == 'zabral':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"SELECT id_group FROM configuration")
                gid = cursor.fetchone()
                cursor.execute(f"SELECT id FROM drivers WHERE username = ?",
                               (callback.from_user.username,))
                res = cursor.fetchone()
                if callback.data == 'driver_accept':

                    cursor.execute(f"UPDATE drivers SET order_status = ? WHERE id = ?",
                                   (0, callback.message.chat.id,))
                    cursor.execute(f"SELECT phone_number FROM making_orders")
                    phone_numbers = cursor.fetchall()
                    for i in range(len(phone_numbers)):
                        if phone_numbers[i][0] in callback.message.text:
                            cursor.execute("UPDATE making_orders SET who_accept = ? WHERE phone_number = ?",
                                           (callback.from_user.username, phone_numbers[i][0]))
                            conn.commit()

                    um = callback.from_user.username
                    cursor.execute(
                        f"SELECT id, msg_id_order, driver_msg_id_order, username FROM making_orders WHERE who_accept = ?",
                        (um,))
                    data = cursor.fetchone()
                    cursor.execute(
                        f"SELECT username, phone_number, fio, car, state_number FROM drivers WHERE username = ?",
                        (um,))
                    driver1 = cursor.fetchone()
                    keyboard = types.InlineKeyboardMarkup()
                    btn_conn = types.InlineKeyboardButton(text='Связь с водителем', url=f'https://t.me/{driver1[0]}')
                    keyboard.add(btn_conn)

                    ordermid = self.bot.edit_message_text(chat_id=data[0],
                                                          message_id=data[1],
                                                          text=f'ℹ️ Ваш заказ принят!'
                                                               f'\nВодитель: {driver1[2]}'
                                                               f'\nАвтомобиль: {driver1[3]} {driver1[4]}'
                                                               f'\nТелефон водителя: {driver1[1]}',
                                                          reply_markup=keyboard
                                                          )
                    cursor.execute(f"UPDATE making_orders SET ordermid = ? WHERE who_accept = ?",
                                   (ordermid.message_id, callback.from_user.username,))
                    self.bot.forward_message(from_chat_id=callback.message.chat.id,
                                             chat_id=res[0],
                                             message_id=callback.message.id
                                             )
                    self.bot.edit_message_text(chat_id=gid[0],
                                               message_id=data[2],
                                               text=f'ℹ️ Заказ принят водителем {callback.from_user.first_name}'
                                               )
                    cursor.execute(f"SELECT message_id, id FROM making_orders WHERE who_accept = ?",
                                   (callback.from_user.username,))
                    geo = cursor.fetchone()
                    if geo[0] is not None:
                        self.bot.forward_message(from_chat_id=geo[1],
                                                 chat_id=res[0],
                                                 message_id=geo[0]
                                                 )
                        self.bot.delete_message(chat_id=gid[0],
                                                message_id=data[2] + 1
                                                )
                        self.bot.delete_message(chat_id=gid[0],
                                                message_id=data[2] + 2
                                                )
                    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
                    btn_conn2 = types.InlineKeyboardButton(text='Связь с заказчиком',
                                                           url=f'https://t.me/{data[3]}'
                                                           )
                    btn_pod = types.InlineKeyboardButton(text='Я подъехал',
                                                         callback_data='driver_pod'
                                                         )
                    btn_zabral = types.InlineKeyboardButton(text='Забрал заказчика',
                                                            callback_data='zabral'
                                                            )
                    keyboard2.add(btn_conn2, btn_pod, btn_zabral)
                    self.bot.send_message(chat_id=res[0],
                                          text=f'ℹ️ {callback.from_user.first_name}, Вы приняли заказ!',
                                          reply_markup=keyboard2
                                          )
                    conn.commit()
                    conn.close()

                if callback.data == 'zabral':
                    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
                    btn_end_order = types.InlineKeyboardButton(text='Завершить поездку',
                                                               callback_data='end_order'
                                                               )
                    keyboard2.add(btn_end_order)
                    self.bot.edit_message_text(chat_id=res[0],
                                               message_id=callback.message.id,
                                               text=f'ℹ️ {callback.from_user.first_name}, Вы забрали заказчика!',
                                               reply_markup=keyboard2
                                               )

            if callback.data == 'end_order':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"SELECT id FROM making_orders WHERE who_accept = ?",
                               (callback.from_user.username,))
                userid = cursor.fetchone()
                cursor.execute(
                    f"SELECT username, phone_number, user_adress, end_adress, sale, message_id FROM making_orders WHERE id = ?",
                    (userid[0],))
                orderd = cursor.fetchone()
                cursor.execute(f"SELECT fio FROM drivers WHERE id = ?",
                               (callback.message.chat.id,))
                fio = cursor.fetchone()
                cdate = date.today()
                now = datetime.now()
                ctime = now.strftime("%H:%M")
                osale = ''
                if orderd[4] is None:
                    osale = '100р'
                cursor.execute(f"INSERT INTO orders"
                               f"(customer_phone,"
                               f"driver,"
                               f"date,"
                               f"time,"
                               f"user_adress,"
                               f"end_adress,"
                               f"sale)"
                               f"VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (orderd[1], fio[0], cdate, ctime, orderd[2], orderd[3], osale))
                cursor.execute(f"SELECT ordermid FROM making_orders WHERE who_accept = ?",
                               (callback.from_user.username,))
                omid = cursor.fetchone()
                keyboard1 = types.InlineKeyboardMarkup(row_width=1)
                btn_mmain = types.InlineKeyboardButton(text='Меню',
                                                       callback_data='main'
                                                       )
                keyboard1.add(btn_mmain)
                self.bot.edit_message_text(chat_id=userid[0],
                                           message_id=omid[0],
                                           text='Заказ завершен!',
                                           reply_markup=keyboard1
                                           )
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_status_1 = types.InlineKeyboardButton(text='Закончить работу',
                                                          callback_data='status_2'
                                                          )
                keyboard.add(btn_status_1)
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, Вы можете принимать заказы!'
                                                f'\nСтатус: "Работаете"',
                                           reply_markup=keyboard
                                           )
                if orderd[5] is not None:
                    self.bot.delete_message(chat_id=callback.message.chat.id,
                                            message_id=callback.message.id - 2
                                            )
                    self.bot.delete_message(chat_id=callback.message.chat.id,
                                            message_id=callback.message.id - 1
                                            )

                cursor.execute(f"UPDATE making_orders SET who_accept = NULL where who_accept = ?",
                               (callback.from_user.username,))

                conn.commit()
                conn.close()

            if callback.data == 'accept_reg':
                try:
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text='ℹ️ Запрос подтвержден!'
                                               )
                    conn = sqlite3.connect('TAXIdata.db')
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT id FROM making_orders WHERE key = '1'")
                    uid = cursor.fetchone()
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    btn_anketa1 = types.InlineKeyboardButton(text='Заполнить анкету',
                                                             callback_data='anketa'
                                                             )
                    keyboard.add(btn_anketa1)
                    self.bot.send_message(chat_id=uid[0],
                                          text=f'ℹ️ Запрос подтвержден!'
                                               f'\nЗаполните анкету водителя',
                                          reply_markup=keyboard
                                          )

                    cursor.execute(f"UPDATE making_orders SET key = NULL")
                    conn.commit()
                    conn.close()
                except:
                    pass

            if callback.data == 'reject_reg':
                try:
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text='ℹ️ Запрос отклонен!'
                                               )
                    conn = sqlite3.connect('TAXIdata.db')
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT id FROM making_orders WHERE key = '1'")
                    uid = cursor.fetchone()
                    self.bot.send_message(chat_id=uid[0],
                                          text=f'ℹ️ Запрос отклонен!'
                                          )
                    cursor.execute(f"UPDATE making_orders SET key = NULL")
                    conn.commit()
                    conn.close()
                except:
                    pass

            if callback.data == 'anketa':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM drivers WHERE id = ?", (callback.message.chat.id,))
                row = cursor.fetchone()
                if row is None:
                    cursor.execute("INSERT INTO drivers (id) VALUES (?)", (callback.message.chat.id,))
                    cursor.execute(
                        f"SELECT username, phone_number FROM making_orders WHERE id = {callback.message.chat.id}")
                    ph = cursor.fetchone()
                    cursor.execute(f"UPDATE drivers SET username = ? WHERE id = ?",
                                   (ph[0], callback.message.chat.id,))
                    cursor.execute(f"UPDATE drivers SET phone_number = ? WHERE id = ?",
                                   (ph[1], callback.message.chat.id,))
                conn.commit()

                keyboard = types.InlineKeyboardMarkup()
                btn_point_name = types.InlineKeyboardButton(text='ФИО',
                                                            callback_data='fio'
                                                            )
                btn_point_car = types.InlineKeyboardButton(text='Машина',
                                                           callback_data='car'
                                                           )
                btn_gosnumber = types.InlineKeyboardButton(text='Госномер авто',
                                                           callback_data='gosnumber'
                                                           )
                btn_done = types.InlineKeyboardButton(text='Готово',
                                                      callback_data='done_anketa'
                                                      )
                keyboard.add(btn_point_name,
                             btn_point_car
                             )
                keyboard.add(btn_gosnumber)
                keyboard.add(btn_done)

                cursor.execute(
                    f"SELECT fio, car, state_number FROM drivers WHERE id = {callback.message.chat.id}")
                data = cursor.fetchone()
                if data[0] is None:
                    name = 'Не указано'
                else:
                    name = data[0]

                if data[1] is None:
                    car = 'Не указано'
                else:
                    car = data[1]

                if data[2] is None:
                    gosnumber = 'Не указано'
                else:
                    gosnumber = data[2]

                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, заполните анкету водителя.'
                                                f'\nФИО: {name}'
                                                f'\nАвтомобиль: {car}'
                                                f'\nГос.номер: {gosnumber}',
                                           reply_markup=keyboard
                                           )

            if callback.data == 'fio':
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, как Вас зовут?'
                                                f'\nФамилия - имя - отчество',
                                           )
                self.bot.register_next_step_handler(callback.message, get_driver_fio)

            if callback.data == 'car':
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, какая у Вас машина?'
                                                f'\nЦвет - марка - модель',
                                           )
                self.bot.register_next_step_handler(callback.message, get_driver_car)

            if callback.data == 'gosnumber':
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, какой у Вас гос.номер автомобиля?'
                                                f'\nЦвет - марка - модель',
                                           )
                self.bot.register_next_step_handler(callback.message, get_driver_gosnumber)

            if callback.data == 'done_anketa':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT fio, car, state_number FROM drivers WHERE id = {callback.message.chat.id}")
                data = cursor.fetchone()
                if data[0] is None or data[1] is None or data[2] is None:
                    keyboard = types.InlineKeyboardMarkup()
                    btn_anketa2 = types.InlineKeyboardButton(text='Заполнить',
                                                             callback_data='anketa'
                                                             )
                    keyboard.add(btn_anketa2)
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text=f'ℹ️ {callback.from_user.first_name}, обязательные данные не заполнены!',
                                               reply_markup=keyboard
                                               )
                else:
                    cursor.execute(f"UPDATE drivers SET status = ? WHERE id = ?",
                                   (0, callback.message.chat.id,))
                    cursor.execute(f"UPDATE drivers SET order_status = ? WHERE id = ?",
                                   (1, callback.message.chat.id,))
                    conn.commit()
                    conn.close()
                    keyboard = types.InlineKeyboardMarkup()
                    btn_start = types.InlineKeyboardButton(text='Начать',
                                                           callback_data='driver_main'
                                                           )
                    keyboard.add(btn_start)
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text=f'ℹ️ {callback.from_user.first_name}, успешная регистрация!',
                                               reply_markup=keyboard
                                               )

            if callback.data == 'driver_main':
                # conn = sqlite3.connect('TAXIdata.db')
                # cursor = conn.cursor()
                # cursor.execute(f"SELECT fio FROM drivers WHERE id = {callback.message.chat.id}")
                # name = cursor.fetchone()
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_status_1 = types.InlineKeyboardButton(text='Работаю',
                                                          callback_data='status_1'
                                                          )
                btn_status_2 = types.InlineKeyboardButton(text='Не работаю',
                                                          callback_data='status_2'
                                                          )
                keyboard.add(btn_status_1,
                             btn_status_2
                             )
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ Вы находитесь в меню водителей'
                                                f'\nВыберите ваш статус',
                                           reply_markup=keyboard
                                           )
            if callback.data == 'status_1' or callback.data == 'status_2':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"UPDATE drivers SET username = ? WHERE id = ?",
                               (callback.from_user.username, callback.message.chat.id))
                conn.commit()
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_work = types.InlineKeyboardButton(text='Начать работу',
                                                      callback_data='status_1',
                                                      )
                btn_no_work = types.InlineKeyboardButton(text='Закончить работу',
                                                         callback_data='status_2',
                                                         )
                if callback.data == 'status_1':
                    cursor.execute(f"UPDATE drivers SET status = ? WHERE id = ?",
                                   (1, callback.message.chat.id,)
                                   )
                    keyboard.add(btn_no_work)
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text=f'ℹ️ {callback.from_user.first_name}, Вы можете принимать заказы!'
                                                    f'\nСтатус: "Работаете"',
                                               reply_markup=keyboard
                                               )

                if callback.data == 'status_2':
                    cursor.execute(f"UPDATE drivers SET status = ? WHERE id = ?",
                                   (0, callback.message.chat.id,)
                                   )
                    cursor.execute(f"UPDATE drivers SET order_status = ? WHERE id = ?",
                                   (0, callback.message.chat.id,)
                                   )

                    keyboard.add(btn_work)
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text=f'ℹ️ {callback.from_user.first_name}, Вы не принимаете заказы!'
                                                    f'\nСтатус: "Не работаете"',
                                               reply_markup=keyboard
                                               )
                conn.commit()
                conn.close()

            if callback.data == 'otchet':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"UPDATE making_orders SET page = ? WHERE id = ?",
                               (0, callback.message.chat.id,))
                cursor.execute(f"SELECT date, time1, time2 FROM making_orders WHERE id = ?",
                               (callback.message.chat.id,))
                ddmm = cursor.fetchone()
                if ddmm[0] is None:
                    dt = 'Не указано'
                else:
                    dt = ddmm[0]
                if ddmm[1] is None:
                    tm1 = 'Не указано'
                else:
                    tm1 = ddmm[1]
                if ddmm[2] is None:
                    tm2 = 'Не указано'
                else:
                    tm2 = ddmm[2]

                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_time = types.InlineKeyboardButton(text='Изменить время',
                                                      callback_data='time'
                                                      )
                btn_date = types.InlineKeyboardButton(text='Изменить дату',
                                                      callback_data='day'
                                                      )
                btn_search = types.InlineKeyboardButton(text='Поиск',
                                                        callback_data='search'
                                                        )
                btn_mmenu = types.InlineKeyboardButton(text='Назад',
                                                       callback_data='main'
                                                       )
                keyboard.add(btn_date,
                             btn_time,
                             btn_search,
                             btn_mmenu
                             )
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, отчёт по каким фильтрам вы хотите получить?'
                                                f'\nДата: {dt}'
                                                f'\nНачальное время: {tm1}'
                                                f'\nКонечное время: {tm2}',
                                           reply_markup=keyboard
                                           )
                conn.close()

            if callback.data == 'search' or callback.data == 'search_next':

                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"SELECT date, time1, time2 FROM making_orders WHERE id = ?",
                               (callback.message.chat.id,))
                prm = cursor.fetchone()

                if callback.data == 'search':


                    keyboard1 = types.InlineKeyboardMarkup()
                    btn_otmm = types.InlineKeyboardButton(text='Назад',
                                                          callback_data='otchet'
                                                          )
                    keyboard1.add(btn_otmm)

                    if prm[0] is None:
                        self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                   message_id=callback.message.id,
                                                   text=f'ℹ️ {callback.from_user.first_name}, дата не указана, либо такой не существует.',
                                                   reply_markup=keyboard1
                                                   )
                    if prm[0] is not None:

                        if prm[1] is None:
                            self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                       message_id=callback.message.id,
                                                       text=f'ℹ️ {callback.from_user.first_name},время не указано, либо такого не существует.',
                                                       reply_markup=keyboard1
                                                       )
                    if prm[0] is not None and prm[1] is not None:
                        cursor.execute(
                            "SELECT * FROM orders WHERE date = ? AND time BETWEEN ? AND '23:59:59'",
                            (prm[0], prm[1],))
                        otc = cursor.fetchall()

                        if prm[0] is not None and prm[1] is not None and prm[2] is not None:
                            cursor.execute(
                                "SELECT order_number FROM orders WHERE date = ? AND time BETWEEN ? AND ?",
                                (prm[0], prm[1], prm[2],))
                            otc = cursor.fetchall()

                        k = 0
                        for row in otc:
                            k += 1
                        keyboard2 = types.InlineKeyboardMarkup()
                        btn_search_next = types.InlineKeyboardButton(text='Показать',
                                                                     callback_data='search_next',
                                                                     )
                        btn_otmena = types.InlineKeyboardButton(text='Назад',
                                                                callback_data='otchet'
                                                                )
                        keyboard2.add(btn_search_next,
                                      btn_otmena
                                      )
                        self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                                   message_id=callback.message.id,
                                                   text=f'ℹ️ {callback.from_user.first_name}, за указанное время было выполнено заказов: {k}',
                                                   reply_markup=keyboard2
                                                   )
                        cursor.execute(f"UPDATE making_orders SET page = ? WHERE id = ?",
                                       (0, callback.message.chat.id,))
                    conn.commit()
                    conn.close()

                if callback.data == 'search_next':

                    conn = sqlite3.connect('TAXIdata.db')
                    cursor = conn.cursor()

                    keyboard1 = types.InlineKeyboardMarkup()
                    btn_next = types.InlineKeyboardButton(text='Следующий заказ',
                                                          callback_data='search_next'
                                                          )
                    btn_otmenna = types.InlineKeyboardButton(text='Назад',
                                                             callback_data='otchet'
                                                             )
                    keyboard1.add(btn_next,
                                 btn_otmenna
                                 )
                    cursor.execute(f"UPDATE making_orders SET page=page+1")
                    conn.commit()
                    cursor.execute(f"SELECT page FROM making_orders WHERE id = ?",
                                   (callback.message.chat.id,))
                    st = cursor.fetchone()
                    print(st[0])
                    if prm[0] is not None and prm[1] is not None:
                        cursor.execute(
                            "SELECT * FROM orders WHERE date = ? AND time BETWEEN ? AND '23:59:59'",
                            (prm[0], prm[1],))
                        otc = cursor.fetchall()

                        if prm[0] is not None and prm[1] is not None and prm[2] is not None:
                            cursor.execute(
                                "SELECT * FROM orders WHERE date = ? AND time BETWEEN ? AND ?",
                                (prm[0], prm[1], prm[2],))
                            otc = cursor.fetchall()

                        k = 0
                        for row in otc:
                            k += 1
                        print(otc[0][1])
                    self.bot.send_message(chat_id=callback.message.chat.id,
                                          text=f'ℹ️ {callback.from_user.first_name}, за указанное время было выполнено заказов: {k}'
                                               f'\nНомер заказа: {otc[st[0]][0]}'
                                               f'\nНомер телефона заказчика: {otc[st[0]][1]}'
                                               f'\nВодитель: {otc[st[0]][2]}'
                                               f'\nДата: {otc[st[0]][3]}'
                                               f'\nВремя: {otc[st[0]][4]}'
                                               f'\nАдрес: {otc[st[0]][5]}'
                                               f'\nКонечный адрес: {otc[st[0]][6]}'
                                               f'\nСтоимость: {otc[st[0]][7]}'
                                               f'\n\nСтраница: {st[0]}/{k}',
                                          reply_markup=keyboard1
                                          )

            if callback.data == 'day':

                keyboard = types.InlineKeyboardMarkup()
                btn_otm = types.InlineKeyboardButton(text='Назад',
                                                     callback_data='otchet'
                                                     )
                keyboard.add(btn_otm)
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, укажите дату в формате'
                                                f'\n"ГГГГ-ММ-ДД", например "2023-11-23"',
                                           reply_markup=None
                                           )
                self.bot.register_next_step_handler(callback.message, get_date)

            if callback.data == 'time':

                keyboard = types.InlineKeyboardMarkup()
                btn_time1 = types.InlineKeyboardButton(text='Начальное время',
                                                       callback_data='time1'
                                                       )
                btn_time2 = types.InlineKeyboardButton(text='Конечное время',
                                                       callback_data='time2'
                                                       )
                btn_otm = types.InlineKeyboardButton(text='Назад',
                                                     callback_data='otchet'
                                                     )
                keyboard.add(btn_otm,
                             btn_time1,
                             btn_time2
                             )
                self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           text=f'ℹ️ {callback.from_user.first_name}, по отдельности укажите время, от которого начинать поиск, и каким заканчивать.',
                                           reply_markup=keyboard
                                           )

            if callback.data == 'time1' or callback.data == 'time2':

                if callback.data == 'time1':
                    keyboard = types.InlineKeyboardMarkup()
                    btn_otm = types.InlineKeyboardButton(text='Назад',
                                                         callback_data='otchet'
                                                         )
                    keyboard.add(btn_otm)
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text=f'ℹ️ {callback.from_user.first_name}, укажите время, от которого начинать поиск.',
                                               reply_markup=None
                                               )
                    self.bot.register_next_step_handler(callback.message, get_time1)

                if callback.data == 'time2':
                    keyboard = types.InlineKeyboardMarkup()
                    btn_otm = types.InlineKeyboardButton(text='Назад',
                                                         callback_data='otchet'
                                                         )
                    keyboard.add(btn_otm)
                    self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                               message_id=callback.message.id,
                                               text=f'ℹ️ {callback.from_user.first_name}, укажите время, которым заканчивать поиск.',
                                               reply_markup=None
                                               )
                    self.bot.register_next_step_handler(callback.message, get_time2)

        """Пользовательская часть"""

        @self.bot.message_handler(content_types=['location'])
        def get_user_adress_auto(message):
            if message.from_user.username is None:
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                btn_how = types.InlineKeyboardButton(text='Как указать?',
                                                     callback_data='how'
                                                     )
                keyboard.add(btn_how)
                self.bot.send_message(chat_id=message.chat.id,
                                      text=f'ℹ️ {message.from_user.first_name}, для корректной работы сервиса у вас ОБЯЗАТЕЛЬНО должно'
                                           f'быть указано имя пользователя!',
                                      reply_markup=keyboard
                                      )
            else:
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM making_orders WHERE id = ?", (message.chat.id,))
                result = cursor.fetchone()
                if result is None:
                    self.bot.send_message(chat_id=message.chat.id,
                                          text=f'{message.from_user.first_name}, для начала работы подтвердите Ваш номер телефона!'
                                          )
                else:

                    if message.location is not None:

                        location = f'{message.location.longitude}, {message.location.latitude}'

                        cursor.execute("UPDATE making_orders SET message_id = ?, user_adress = ? WHERE id = ?",
                                       (message.message_id, location, message.chat.id)
                                       )
                        try:
                            cursor.execute(
                                f"SELECT del_msg_id, del_msg_id2 FROM making_orders WHERE id = {message.chat.id}")
                            delmsg = cursor.fetchone()
                            self.bot.delete_message(chat_id=message.chat.id,
                                                    message_id=delmsg[0]
                                                    )
                            self.bot.delete_message(chat_id=message.chat.id,
                                                    message_id=delmsg[1]
                                                    )
                        except:
                            pass
                        conn.commit()
                        conn.close()
                        keyboard = types.InlineKeyboardMarkup(row_width=2)
                        btn_next = types.InlineKeyboardButton(text='Далее ▶️',
                                                              callback_data='order'
                                                              )
                        keyboard.add(btn_next)
                        self.bot.send_message(chat_id=message.chat.id,
                                              text=f'ℹ️ {message.from_user.first_name}, Ваш адрес получен',
                                              reply_markup=keyboard
                                              )

        def get_user_adress_manually(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()

            cursor.execute(f"SELECT del_msg_id FROM making_orders WHERE id = {message.chat.id}")
            delmsg = cursor.fetchone()
            try:
                self.bot.delete_message(chat_id=message.chat.id,
                                        message_id=delmsg[0]
                                        )
            except:
                pass
            cursor.execute("UPDATE making_orders SET user_adress = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup(row_width=2)
            btn_next = types.InlineKeyboardButton(text='Далее ▶️',
                                                  callback_data='order'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text=f'ℹ️ {message.from_user.first_name}, Ваш адрес получен',
                                  reply_markup=keyboard
                                  )

            conn.close()

        def get_end_adress(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT del_msg_id FROM making_orders WHERE id = {message.chat.id}")
            delmsg = cursor.fetchone()
            try:
                self.bot.delete_message(chat_id=message.chat.id,
                                        message_id=delmsg[0]
                                        )
            except:
                pass
            cursor.execute("UPDATE making_orders SET end_adress = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            btn_next = types.InlineKeyboardButton(text='Далее ▶️',
                                                  callback_data='order'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text=f'ℹ️ {message.from_user.first_name}, конечный адрес получен',
                                  reply_markup=keyboard
                                  )

        def message_for_driver(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT del_msg_id FROM making_orders WHERE id = {message.chat.id}")
            delmsg = cursor.fetchone()
            try:
                self.bot.delete_message(chat_id=message.chat.id,
                                        message_id=delmsg[0]
                                        )
            except:
                pass
            cursor.execute("UPDATE making_orders SET message = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='order'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text=f'ℹ️ {message.from_user.first_name}, сообщение будет доставлено водителю.',
                                  reply_markup=keyboard
                                  )

        def give_user_sale(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT del_msg_id FROM making_orders WHERE id = {message.chat.id}")
            delmsg = cursor.fetchone()
            try:
                self.bot.delete_message(chat_id=message.chat.id,
                                        message_id=delmsg[0]
                                        )
            except:
                pass
            cursor.execute("UPDATE making_orders SET sale = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='order'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text=f'ℹ️ {message.from_user.first_name}, стоимость указана.',
                                  reply_markup=keyboard
                                  )

        """Водительская часть"""

        def get_driver_fio(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE drivers SET fio = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup()
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='anketa'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Отлично!',
                                  reply_markup=keyboard
                                  )

        def get_driver_car(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE drivers SET car = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup()
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='anketa'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Отлично!',
                                  reply_markup=keyboard
                                  )

        def get_driver_gosnumber(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE drivers SET state_number = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup()
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='anketa'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Отлично!',
                                  reply_markup=keyboard
                                  )

        def get_date(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE making_orders SET date = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup()
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='otchet'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Дата указана!',
                                  reply_markup=keyboard
                                  )

        def get_time1(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE making_orders SET time1 = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup()
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='otchet'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Время указано!',
                                  reply_markup=keyboard
                                  )

        def get_time2(message):

            conn = sqlite3.connect('TAXIdata.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE making_orders SET time2 = ? WHERE id = ?",
                           (message.text, message.chat.id)
                           )
            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup()
            btn_next = types.InlineKeyboardButton(text='Далее',
                                                  callback_data='otchet'
                                                  )
            keyboard.add(btn_next)
            self.bot.send_message(chat_id=message.chat.id,
                                  text='Время указано!',
                                  reply_markup=keyboard
                                  )

        @self.bot.message_handler(commands=['regdriver'])
        def regdriver(message):
            try:
                conn = sqlite3.connect('TAXIdata.db')
                cursor = conn.cursor()
                cursor.execute(f"UPDATE making_orders SET key = ? WHERE id = ?",
                               (1, message.chat.id,))
                self.bot.send_message(chat_id=message.chat.id,
                                      text=f'ℹ️ {message.from_user.first_name}, запрос успешно отправлен администратору!'
                                           f'\nЯ уведомлю вас, когда администратор подтвердит его..'
                                      )
                cursor.execute(f"SELECT id FROM making_orders WHERE permissions = 'administrator'")
                pid = cursor.fetchone()
                cursor.execute(f"SELECT username FROM making_orders WHERE id = {message.chat.id}")
                um = cursor.fetchone()
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                btn_accept_reg = types.InlineKeyboardButton(text='Подтвердить',
                                                            callback_data='accept_reg'
                                                            )
                btn_reject_reg = types.InlineKeyboardButton(text='Отклонить',
                                                            callback_data='reject_reg'
                                                            )
                keyboard.add(btn_accept_reg,
                             btn_reject_reg
                             )
                self.bot.send_message(chat_id=pid[0],
                                      text=f'ℹ️ {message.from_user.first_name}, было запрошено подтверждение пользователем @{um[0]}.',
                                      reply_markup=keyboard
                                      )
                conn.commit()
                conn.close()
            except:
                pass



        self.bot.polling(none_stop=True)


if __name__ == "__main__":
    # try:
    token = config_taxibot.token
    bot = Bot(token)
    bot.start()

#         while True:
#             try:
#                 await self.bot.polling()
#             except Exception:
#                 await asyncio.sleep(5)
#
#
#
# if __name__ == "__main__":
#     token = config_taxibot.token
#     bot = Bot(token)
#     asyncio.run(bot.start())
