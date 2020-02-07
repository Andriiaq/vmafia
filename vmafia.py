# -*- coding: utf-8 -*-
import config
import telebot
from telebot import types
import psycopg2

DATABASE_URL = config.database_url
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

bot = telebot.TeleBot(config.token)

GROUP1_ID1 = config.group1_id
GROUP2_ID2 = config.group2_id

#
# Актив
temp_uids = []
uids = []
cur.execute("SELECT uids FROM active")
uids = [a[0] for a in cur.fetchall()]
print(uids)


# cur.execute("DELETE FROM active")
cur.execute("SELECT msgid FROM delmsg")
cur.execute("DELETE FROM delmsg")
conn.commit()


@bot.message_handler(commands=['актив'])
def active(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id,
                         '<a href="tg://user?id={}">{}</a>, чуєш, злодіяка, цей бот працює лише у чаті @vmafia.😁'.format(
                             msg.from_user.id, msg.from_user.first_name), parse_mode="HTML")
    else:
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
                    link += '<a href="tg://user?id={id}">{name}</a>, '.format(id=uid,
                                                                              name=bot.get_chat_member(msg.chat.id,
                                                                                                       uid).user.first_name)
                    i += 1
                    if i % 5 == 0:
                        bot.send_message(msg.chat.id, link[:-2], parse_mode='html')
                        link = ''
                if link:
                    bot.send_message(msg.chat.id, link[:-2], parse_mode='html')
                bot.send_message(msg.chat.id, '‌‌‎‌‌‎', parse_mode='html')
            bot.send_message(msg.chat.id,
                             'Хочеш, щоб тебе також <b>кликали в гру</b>? <b>Додай</b> або <b>видали</b> себе сам. Обіцяємо, що <b>надокучати не будемо.</b> ♥',
                             reply_markup=keyboard, parse_mode='html')
        else:
            cur.execute("SELECT msgid FROM delmsg")
            msgid = cur.fetchone()
            print(msgid)
            bot.delete_message(msg.chat.id, msg.message_id)
            if not msgid == None:
                bot.delete_message(msg.chat.id, msgid)
                cur.execute("DELETE FROM delmsg")
                conn.commit()
            msgadm = bot.send_message(msg.chat.id,
                                      '<a href="tg://user?id={}">{}</a>, актив можуть надсилати лише адміни.😁'.format(
                                          msg.from_user.id, msg.from_user.first_name), parse_mode="HTML")
            cur.execute("INSERT INTO delmsg (msgid) VALUES (%s)", [msgadm.message_id])
            conn.commit()
            print(msgid)


@bot.callback_query_handler(func=lambda c: True)
def active(call):
    uid = call.from_user.id
    temp_uid = call.from_user.id
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
                        link += '<a href="tg://user?id={id}">{name}</a>, '.format(name=bot.get_chat_member(call.message.chat.id, temp_uid).user.first_name, id=temp_uid)
                    bot.edit_message_text(text='''Додано в <b>наступний</b> актив:
'''+ link[:-2], parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text='Ти не учасник чату.')


#
# Команди

@bot.message_handler(content_types=["new_chat_members"])
def triggers(msg):
    if not msg.new_chat_member.is_bot == True:
        cid = msg.chat.id
        uid = msg.new_chat_member.id
        user_name = msg.new_chat_member.first_name
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
    uid = msg.left_chat_member.id
    if uid in uids:
        cur.execute('DELETE FROM active WHERE uids = %s', [uid])
        uids.remove(uid)
        conn.commit()

bot.polling(none_stop=True)