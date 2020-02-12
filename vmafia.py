# -*- coding: utf-8 -*-
# Python File
import config
import text
# Python Add-ons
import sys
import time
import psycopg2
import telebot
from telebot import types

# Config
bot = telebot.TeleBot(config.token)

DATABASE_URL = config.database_url
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

GROUP_ID = config.group_id


#
#
# Команди

@bot.message_handler(regexp='!testall')
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        cur.execute("SELECT list FROM all_uids")
        list_uids = [b[0] for b in cur.fetchall()]
        link = ''
        for list_uid in list_uids:
            link += '<a href="tg://user?id={id}">{name}</a>, '.format(id=list_uid,
                                                                      name=bot.get_chat_member(msg.chat.id, list_uid).user.first_name)
        if link:
            bot.send_message(msg.chat.id, link[:-2], parse_mode='html')

@bot.message_handler(regexp='!addall')
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        cur.execute("SELECT list FROM all_uids")
        cur.execute("DELETE FROM active")  # Видалити весь актив
        cur.execute("INSERT INTO active (uids) SELECT list FROM all_uids")
        conn.commit()
        msg_delete = bot.send_message(msg.chat.id, text.alladdact)
        time.sleep(5)
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.delete_message(msg.chat.id, msg_delete.message_id)

@bot.message_handler(commands=['гайд', 'guide'])
def triggers(msg):
    cid = msg.chat.id
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text='Читати правила', url='https://t.me/mafia_pravyla')
    keyboard.add(url_button)
    msgbotdel = bot.send_message(cid, text=text.guide, parse_mode='HTML', reply_markup=keyboard)
    ##### Вибрати та видалити id повідомлення
    cur.execute("SELECT msg3 FROM delmsg")
    delid = cur.fetchone()
    if not None in delid:
        try:
            bot.delete_message(msg.chat.id, delid)
        except Exception:
            cur.execute("UPDATE delmsg SET msg3 = NULL")
    cur.execute("UPDATE delmsg SET msg3 = %s", [msgbotdel.message_id])
    conn.commit()
    ##### Зберегти id поста


#
#
# Актив

temp_uids = []

# cur.execute("DELETE FROM active")  # Удалить весь актив!!
cur.execute("SELECT uids FROM active")
uids = [a[0] for a in cur.fetchall()]
print(uids)

cur.execute("SELECT list FROM all_uids")
list_uids = [b[0] for b in cur.fetchall()]
print(list_uids)
conn.commit()


#
# Вхід–Вихід

@bot.message_handler(content_types=["new_chat_members"])
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")
    else:
        if not msg.new_chat_member.is_bot == True:
            uid = msg.new_chat_member.id
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Читати правила", url="https://t.me/mafia_pravyla")
            keyboard.add(url_button)
            msgbotdel = bot.send_message(msg.chat.id,
                                         text=text.hello.format(uid, msg.new_chat_member.first_name),
                                         parse_mode="HTML", reply_markup=keyboard)
            if not uid in uids:
                cur.execute("INSERT INTO active (uids) VALUES (%s)", [uid])
                cur.execute("INSERT INTO all_uids (list) VALUES (%s)", [uid])
                uids.append(uid)
            ##### Вибрати та видалити id повідомлення
            cur.execute("SELECT msg2 FROM delmsg")
            delid = cur.fetchone()
            if not None in delid:
                try:
                    bot.delete_message(msg.chat.id, delid)
                except Exception:
                    cur.execute("UPDATE delmsg SET msg2 = NULL")
            cur.execute("UPDATE delmsg SET msg2 = %s", [msgbotdel.message_id])
            conn.commit()
            ##### Зберегти id поста


@bot.message_handler(content_types=["left_chat_member"])
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")
    else:
        uid = msg.left_chat_member.id
        if uid in uids:
            cur.execute('DELETE FROM active WHERE uids = %s', [uid])
            cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
            conn.commit()
            uids.remove(uid)


@bot.message_handler(commands=['актив', 'active'])
def active(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            temp_uids.clear()
            bot.send_message(msg.chat.id, text=text.actext1, parse_mode='html')
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(
                types.InlineKeyboardButton(text=text.activebtn1, callback_data='text1')
            )
            keyboard.row(
                types.InlineKeyboardButton(text=text.activebtn2, callback_data='text2')
            )
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
                bot.send_message(msg.chat.id, text=text.actext2, parse_mode='html')
            bot.send_message(msg.chat.id, text=text.actext3, reply_markup=keyboard, parse_mode='html')
        else:
            msgbotdel = bot.send_message(msg.chat.id, text=text.actonlyadm.format(msg.from_user.id), parse_mode="HTML")
            bot.delete_message(msg.chat.id, msg.message_id)
            ##### Вибрати та видалити id повідомлення
            cur.execute("SELECT msg1 FROM delmsg")
            delid = cur.fetchone()
            if not None in delid:
                try:
                        bot.delete_message(msg.chat.id, delid)
                except Exception:
                    cur.execute("UPDATE delmsg SET msg1 = NULL")
            cur.execute("UPDATE delmsg SET msg1 = %s", [msgbotdel.message_id])
            conn.commit()
            ##### Зберегти id поста


@bot.callback_query_handler(func=lambda c: True)
def active(call):
    uid = call.from_user.id
    temp_uid = call.from_user.id
    link = ""
    if bot.get_chat_member(call.message.chat.id, call.from_user.id).status == 'left':
        bot.answer_callback_query(callback_query_id=call.id, text='Щоб долучитися, потрібно приєднатися до чату.')
    else:
        if call.data == 'text1':
            if uid in uids:
                bot.answer_callback_query(callback_query_id=call.id, text='Ти вже є у активі.')
            else:
                cur.execute("INSERT INTO active (uids) VALUES (%s)", [call.from_user.id])
                conn.commit()
                uids.append(uid)
                bot.answer_callback_query(callback_query_id=call.id, text='Тебе додано в наступний актив.')
                temp_uids.append(temp_uid)
                for temp_uid in temp_uids:
                    link += '<a href="tg://user?id={id}">{name}</a>, '.format(
                        name=bot.get_chat_member(call.message.chat.id, temp_uid).user.first_name, id=temp_uid)
                bot.edit_message_text(text='''Долучились в <b>наступний</b> актив:
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
                        bot.edit_message_text(text=text.actext2, parse_mode='HTML', chat_id=call.message.chat.id,
                                              message_id=call.message.message_id - 1)
                if not len(temp_uids) == 0:
                    for temp_uid in temp_uids:
                        link += '<a href="tg://user?id={id}">{name}</a>, '.format(
                            name=bot.get_chat_member(call.message.chat.id, temp_uid).user.first_name, id=temp_uid)
                    bot.edit_message_text(text='''Долучились в <b>наступний</b> актив: 
''' + link[:-2], parse_mode='HTML', chat_id=call.message.chat.id, message_id=call.message.message_id - 1)

@bot.message_handler(regexp='!add')
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id),
                         parse_mode="HTML")
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            uid = msg.reply_to_message.from_user.id
            print(uid)
            if not uid in uids:
                if bot.get_chat_member(GROUP_ID, uid).status == 'member':
                    msg_delete = bot.send_message(msg.chat.id, text.addact)
                    cur.execute("INSERT INTO active (uids) VALUES (%s)", [uid])
                    cur.execute("INSERT INTO all_uids (list) VALUES (%s)", [uid])
                    uids.append(uid)
                    time.sleep(3)
                    bot.delete_message(msg.chat.id, msg.message_id)
                    bot.delete_message(msg.chat.id, msg_delete.message_id)
                else:
                    msg_delete = bot.send_message(msg.chat.id, text.nochatmember)
                    time.sleep(3)
                    bot.delete_message(msg.chat.id, msg.message_id)
                    bot.delete_message(msg.chat.id, msg_delete.message_id)
            else:
                msg_delete = bot.send_message(msg.chat.id, text.noaddact)
                time.sleep(3)
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.delete_message(msg.chat.id, msg_delete.message_id)

@bot.message_handler(regexp='!del')
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia)
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            uid = msg.reply_to_message.from_user.id
            print(uid)
            if uid in uids:
                msg_delete = bot.send_message(msg.chat.id, text.delact)
                cur.execute('DELETE FROM active WHERE uids = %s', [uid])
                cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
                conn.commit()
                uids.remove(uid)
                time.sleep(3)
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.delete_message(msg.chat.id, msg_delete.message_id)
            else:
                msg_delete = bot.send_message(msg.chat.id, text.delact)
                time.sleep(3)
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.delete_message(msg.chat.id, msg_delete.message_id)

#
# kick ban COMBOT

@bot.message_handler(regexp='!г')
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        bot.delete_message(msg.chat.id, msg.message_id)
        next_game_message = bot.send_message(msg.chat.id, text.nextgame, parse_mode="HTML")
        bot.pin_chat_message(msg.chat.id, next_game_message.message_id)


@bot.message_handler(regexp='!ban')
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            uid = msg.reply_to_message.from_user.id
            print(uid)
            if uid in uids:
                cur.execute('DELETE FROM active WHERE uids = %s', [uid])
                cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
                conn.commit()
                uids.remove(uid)

@bot.message_handler(regexp='!kick')
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")
    else:
        uid = msg.reply_to_message.from_user.id
        print(uid)
        if uid in uids:
            cur.execute('DELETE FROM active WHERE uids = %s', [uid])
            cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
            conn.commit()
            uids.remove(uid)

@bot.message_handler(commands=['kick', 'ban'])
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            uid = msg.reply_to_message.from_user.id
            print(uid)
            if uid in uids:
                cur.execute('DELETE FROM active WHERE uids = %s', [uid])
                cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
                conn.commit()
                uids.remove(uid)

#
# kick ban COMBOT


bot.polling(none_stop=True)