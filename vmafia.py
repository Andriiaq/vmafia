# -*- coding: utf-8 -*-
import config
import telebot
from telebot import types
import psycopg2
DATABASE_URL = 'postgres://wommmmevwhfpyr:1b5d073a1c84d111c9969c64494ba324f5260049ce5b9f0672885ded3616fcbd@ec2-54-246-89-234.eu-west-1.compute.amazonaws.com:5432/d44hnvrm79hna6'
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

bot = telebot.TeleBot(config.token)


#
# Актив
temp_uids = []
uids = []
cur.execute("SELECT uids FROM active")
uids = [a[0] for a in cur.fetchall()]
print(uids)
all_uids = []
cur.execute("SELECT all_uids FROM all_members")
print(all_uids)
all_uids = [b[0] for b in cur.fetchall()]


step = {}
true = ""


@bot.message_handler(commands=['add'])
def subscribe_chat(message):
        step[true] = 1
        bot.reply_to(message, "Перешліть повідомлення користувача, якого ви хочете додати в актив.")

#@bot.message_handler(func=lambda message: step.get(true) == 1)
#def add_user_active(m):
#    if m.forward_from:
#        print(step.get(true))
#        fw_user = {'name': m.forward_from.first_name, 'id': m.forward_from.id}
#        cur.execute("INSERT INTO active (uids) VALUES (%s)", [call.from_user.id])
#        conn.commit()
#        uids.append(user)
#        bot.reply_to(m, "Користувача додано в актив.")
#        step[true] = 0
#    else:
#        print('Not forward message')
#        bot.reply_to(m, "Користувача не додано. Спробуйте ще раз.")
#        step[true] = 0

@bot.message_handler(commands=['add2'])
def subscribe_chat(message):
        step[true] = 1
        bot.reply_to(message, "Перешліть повідомлення користувача, якого ви хочете додати в актив.")

@bot.message_handler(func=lambda message: step.get(true) == 1)
def add_user_active(m):
#    if 1 not qwe:
    if m.text == 'f({x, })':
        print("1121")
        uids.append(user)
        bot.reply_to(m, "Користувачів додано в актив.")
        step[true] = 0
        ids = [m.text]
        new_ids = [f'({x})' for x in ids]
        print(new_ids)
        s = ','.join(new_ids)
        print(s)
        query = cur.execute("INSERT INTO active (uids) VALUES {}".format(s))
        conn.commit()
#    else 1 == qwe:
#        print('Not forward message')
#        bot.reply_to(m, "Користувачів не додано. Спробуйте ще раз.")
#        step[true] = 0


@bot.message_handler(regexp='!r')
def triggers(msg):
    cid = msg.chat.id
    id = msg.from_user.id
    user_name = msg.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    user = {'name': msg.from_user.first_name, 'id': msg.from_user.id}
    test = cur.execute('DELETE FROM active')
    test2 = cur.execute('DELETE FROM all_members')
    print(test)
    print(test2)
    conn.commit()
    bot.send_message(cid, text='''\
    Актив очищено. 🌹
    '''.format(id, user_name), parse_mode='HTML', reply_markup=keyboard)

@bot.message_handler(commands=['1'])
def active(msg):
    print(msg.text)


@bot.message_handler(commands=['актив'])
def active(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(msg.chat.id)]
    if msg.from_user.id in admins:
        temp_uids.clear()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton(text='Так, покличте мене 🥰', callback_data='text1')
        )
        keyboard.row(
            types.InlineKeyboardButton(text='Не кличте мене 😕‍', callback_data='text2')
        )
        bot.send_message(msg.chat.id, text='<b>Шооооооооой</b>, до бою, <b>Мирнi</b>! 😂🐒♥️', parse_mode='html')
        if len(uids) == 0:
            bot.send_message(msg.chat.id, 'Будь першим')
        else:
            i = 0
            link = ''
            for uid in uids:
                link += '<a href="tg://user?id={id}">{name}</a>, '.format(id=uid, name=bot.get_chat_member(msg.chat.id, uid).user.first_name)
                i += 1
                if i % 5 == 0:
                    bot.send_message(msg.chat.id, link[:-2], parse_mode='html')
                    link = ''
            if link:
                bot.send_message(msg.chat.id, link[:-2], parse_mode='html')
            bot.send_message(msg.chat.id, '‌‌‎‌‌‎', parse_mode='html')
        bot.send_message(msg.chat.id, 'Тест ДеплоюХочеш, щоб тебе також <b>кликали в гру</b>? <b>Додай</b> або <b>видали</b> себе сам. Обіцяємо, що <b>надокучати не будемо.</b> ♥', reply_markup=keyboard, parse_mode='html')
    else:
        print('you not admin')

@bot.callback_query_handler(func=lambda c: True)
def active(call):
    uid = call.from_user.id
    temp_uid = call.from_user.id
    temp_uname = bot.get_chat_member(call.message.chat.id, call.from_user.id).user.first_name
    link = ""
    if call.data == 'text1':
        if uid in uids:
            bot.answer_callback_query(callback_query_id=call.id, text='Ви вже є у списку.')
        else:
            cur.execute("INSERT INTO active (uids) VALUES (%s)", [call.from_user.id])
            conn.commit()
            uids.append(uid)
            bot.answer_callback_query(callback_query_id=call.id, text='Вас додано до списку.')
            temp_uids.append(temp_uid)
            for temp_uid in temp_uids:
                link += '<a href="tg://user?id={id}">{name}</a>, '.format(name=bot.get_chat_member(call.message.chat.id, temp_uid).user.first_name, id=temp_uid)
            bot.edit_message_text(text='''Додано в <b>наступний</b> актив:
''' + link[:-2], parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    elif call.data == 'text2':
        if len(uids) == 0 or uid not in uids:
            bot.answer_callback_query(callback_query_id=call.id, text='Вас немає в наступному активі.')
        else:
            cur.execute('DELETE FROM active WHERE uids = %s', [call.from_user.id])
            conn.commit()
            uids.remove(uid)
            bot.answer_callback_query(callback_query_id=call.id, text='Вас видалено з наступного активу.')
            if temp_uid in temp_uids:
                temp_uids.remove(temp_uid)
                if len(temp_uids) == 0:
                    bot.edit_message_text(text='‌‌‎‌‌‎', parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
            if not len(temp_uids) == 0:
                for temp_uid in temp_uids:
                    link += '<a href="tg://user?id={id}">{name}</a>, '.format(name=temp_uname, id=temp_uid)
                bot.edit_message_text(text='''Додано в <b>наступний</b> актив:
'''+ link[:-2], parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)


#
# Команди

@bot.message_handler(regexp='!гайд')
def triggers(msg):
    cid = msg.chat.id
    id = msg.from_user.id
    user_name = msg.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text='Читати правила гри', url='https://t.me/mafia_pravyla/14')
    keyboard.add(url_button)
    bot.send_message(cid, text='''\
    Якшо ти новий гравець, то натисни нижче, щоб прочитати правила гри. 🌹
    '''.format(id, user_name), parse_mode='HTML', reply_markup=keyboard)


@bot.message_handler(regexp="!ходи")
def triggers(msg):
    cid = msg.chat.id
    id = msg.from_user.id
    user_name = msg.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Виконати дії", url="https://t.me/TrueMafiaBot")
    keyboard.add(url_button)
    bot.send_message(cid, text='''\
*Увага! Зараз ніч!* Гравці виконують *таємні дії* в діалозі з ботом @TrueMafiaBot, а в чаті панує повна тиша(бот видаляє повідомлення та тимчасово блокує за спроби написати).
    '''.format(id, user_name), parse_mode="Markdown", reply_markup=keyboard)


@bot.message_handler(content_types=["new_chat_members"])
def triggers(msg):
    cid = msg.chat.id
    uid = msg.from_user.id
    user_name = msg.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Читати правила гри", url="https://t.me/mafia_pravyla/14")
    keyboard.add(url_button)
    bot.send_message(cid, text='''\
А ну всі швиденько <b>привітали нового гравця</b> <a href="tg://user?id={}">{}</a>! 🌝  Заходь та влаштовуйся позручніше, <b>бро</b>! ♥

<b>Раді тобі</b> у нашому дружньому чаті. Тут лише <b>хороші</b> люди та приємна <b>атмосфера. Основна гра</b> у мафію починається <b>о 21:00</b>. Долучайся! 🌹
        '''.format(uid, user_name), parse_mode="HTML", reply_markup=keyboard)
    cur.execute("INSERT INTO all_members (all_uids) VALUES (%s)", [uid])

    conn.commit()
    all_uids.append(uid)
    print(all_uids)

@bot.message_handler(content_types=["left_chat_member"])
def triggers(msg):
    uid = msg.from_user.id
    cur.execute('DELETE FROM all_members WHERE all_uids = %s', [uid])
    cur.execute('DELETE FROM active WHERE uids = %s', [uid])
    all_uids.remove(uid)
    conn.commit()
    if uid in uids:
        cur.execute('DELETE FROM active WHERE uids = %s', [uid])
        uids.remove(uid)
    print(all_uids)

bot.polling(none_stop=True)