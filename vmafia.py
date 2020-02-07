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
#print(uids)
all_uids = []
cur.execute("SELECT all_uids FROM all_members")
#print(all_uids)
all_uids = [b[0] for b in cur.fetchall()]

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
        bot.send_message(msg.chat.id, 'Хочеш, щоб тебе також <b>кликали в гру</b>? <b>Додай</b> або <b>видали</b> себе сам. Обіцяємо, що <b>надокучати не будемо.</b> ♥', reply_markup=keyboard, parse_mode='html')
    else:
        bot.send_message(msg.chat.id, 'Актив можуть надсилати лише адміни.😁')

@bot.callback_query_handler(func=lambda c: True)
def active(call):
    uid = call.from_user.id
    temp_uid = call.from_user.id
    temp_uname = bot.get_chat_member(call.message.chat.id, call.from_user.id).user.first_name
    link = ""
    if not bot.get_chat_member(call.message.chat.id, call.from_user.id).status == 'left':
        if call.data == 'text1':
            if uid in uids:
                bot.answer_callback_query(callback_query_id=call.id, text='Ти вже є у списку.')
            else:
                cur.execute("INSERT INTO active (uids) VALUES (%s)", [call.from_user.id])
                conn.commit()
                uids.append(uid)
                bot.answer_callback_query(callback_query_id=call.id, text='Тебе додано до списку.')
                temp_uids.append(temp_uid)
                for temp_uid in temp_uids:
                    link += '<a href="tg://user?id={id}">{name}</a>, '.format(name=bot.get_chat_member(call.message.chat.id, temp_uid).user.first_name, id=temp_uid)
                bot.edit_message_text(text='''Додано в <b>наступний</b> актив:
''' + link[:-2], parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        elif call.data == 'text2':
            if len(uids) == 0 or uid not in uids:
                bot.answer_callback_query(callback_query_id=call.id, text='Тебе немає в наступному активі.')
            else:
                cur.execute('DELETE FROM active WHERE uids = %s', [call.from_user.id])
                conn.commit()
                uids.remove(uid)
                bot.answer_callback_query(callback_query_id=call.id, text='Тебе видалено з наступного активу.')
                if temp_uid in temp_uids:
                    temp_uids.remove(temp_uid)
                    if len(temp_uids) == 0:
                        bot.edit_message_text(text='‌‌‎‌‌‎', parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
                if not len(temp_uids) == 0:
                    for temp_uid in temp_uids:
                        link += '<a href="tg://user?id={id}">{name}</a>, '.format(name=temp_uname, id=temp_uid)
                    bot.edit_message_text(text='''Додано в <b>наступний</b> актив:
'''+ link[:-2], parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text='Ти не учасник чату.')


#
# Команди

@bot.message_handler(regexp='!гайд')
def triggers(msg):
    cid = msg.chat.id
    id = msg.from_user.id
    user_name = msg.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text='Читати правила гри', url='https://t.me/vmbook')
    keyboard.add(url_button)
    bot.send_message(cid, text='''\
    Якщо ти новий гравець, то натисни нижче, щоб прочитати правила гри. 🌹
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
    url_button = types.InlineKeyboardButton(text="Читати правила", url="https://t.me/vmbook")
    keyboard.add(url_button)
    bot.send_message(cid, text='''\
А ну всі швиденько <b>привітали нового гравця</b> <a href="tg://user?id={}">{}</a>! 🌝  Заходь та влаштовуйся позручніше, <b>бро</b>! ♥

<b>Раді тобі</b> у нашому дружньому чаті. Тут лише <b>хороші</b> люди та приємна <b>атмосфера. Основна гра</b> у мафію починається <b>о 21:00</b>. Долучайся! 🌹
        '''.format(uid, user_name), parse_mode="HTML", reply_markup=keyboard)
    cur.execute("INSERT INTO active (uids) VALUES (%s)", [uid])
    conn.commit()
    uids.append(uid)

@bot.message_handler(content_types=["left_chat_member"])
def triggers(msg):
    uid = msg.from_user.id
    if uid in all_uids:
        cur.execute('DELETE FROM all_members WHERE all_uids = %s', [uid])
        all_uids.remove(uid)
    if uid in uids:
        cur.execute('DELETE FROM active WHERE uids = %s', [uid])
        uids.remove(uid)
    conn.commit()


bot.polling(none_stop=True)