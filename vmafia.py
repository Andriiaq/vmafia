# -*- coding: utf-8 -*-
# Python File
import config
import text
# Python Add-ons
import threading
import psycopg2
import telebot
from telebot import types
import schedule
import time

# Config PostgreSQL
bot = telebot.TeleBot(config.token)

DATABASE_URL = config.database_url
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

GROUP_ID = config.group_id
GROUP_ID_ACTIVE = config.group_id_active

#
#
# Active
# cur.execute("DELETE FROM active")  # Удалить весь актив!!
temp_uids = []
cur.execute("SELECT uids FROM active")
uids = [a[0] for a in cur.fetchall()]

cur.execute("SELECT list FROM all_uids")
all_uids = [b[0] for b in cur.fetchall()]

cur.execute("SELECT uids_admins FROM active_admins")
uids_admins = [a[0] for a in cur.fetchall()]

conn.commit()
print(text.test_bot)


@bot.message_handler(commands=['актив', 'active'])
def active(msg):
    if msg.chat.id == GROUP_ID:
        if not bot.get_chat_member(GROUP_ID_ACTIVE, msg.from_user.id).status == 'left':
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
            msg_delete = bot.send_message(msg.chat.id, text=text.onlyact.format(msg.from_user.id), parse_mode="HTML")
            time.sleep(5)
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.delete_message(msg.chat.id, msg_delete.message_id)
    ### АКТИВ АДМІНСЬКИЙ
    elif msg.chat.id == GROUP_ID_ACTIVE:
        i = 0
        link = ''
        for uid in uids_admins:
            link += '<a href="tg://user?id={id}">{name}</a>, '.format(id=uid, name=bot.get_chat_member(msg.chat.id,
                                                                                                       uid).user.first_name)
            i += 1
            if i % 5 == 0:
                bot.send_message(msg.chat.id, link[:-2], parse_mode='html')
                link = ''
        if link:
            bot.send_message(msg.chat.id, link[:-2], parse_mode='html')
    else:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")


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


#
#
# Add/del active

@bot.message_handler(commands=['add_all'])
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        cur.execute("SELECT list FROM all_uids")
        cur.execute("DELETE FROM active")  # Видалити весь актив
        cur.execute("INSERT INTO active (uids) SELECT list FROM all_uids")
        conn.commit()
        bot.send_message(msg.chat.id, text.alladdact)


@bot.message_handler(commands=['add'])
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
        else:
            msg_delete = bot.send_message(msg.chat.id, text=text.onlyadm.format(msg.from_user.id), parse_mode="HTML")
            time.sleep(5)
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.delete_message(msg.chat.id, msg_delete.message_id)


@bot.message_handler(commands=['del_forever'])
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia)
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            uid = msg.reply_to_message.from_user.id
            print(uid)
            if uid in all_uids:
                msg_delete = bot.send_message(msg.chat.id, text.delact)
                cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
                if uid in uids:
                    cur.execute('DELETE FROM active WHERE uids = %s', [uid])
                    uids.remove(uid)
                conn.commit()
                time.sleep(3)
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.delete_message(msg.chat.id, msg_delete.message_id)
            else:
                msg_delete = bot.send_message(msg.chat.id, text.delact)
                time.sleep(3)
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.delete_message(msg.chat.id, msg_delete.message_id)
        else:
            msg_delete = bot.send_message(msg.chat.id, text=text.onlyadm.format(msg.from_user.id), parse_mode="HTML")
            time.sleep(5)
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.delete_message(msg.chat.id, msg_delete.message_id)


@bot.message_handler(commands=['del'])
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia)
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            uid = msg.reply_to_message.from_user.id
            if uid in uids:
                msg_delete = bot.send_message(msg.chat.id, text.delact)
                cur.execute('DELETE FROM active WHERE uids = %s', [uid])
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
        else:
            msg_delete = bot.send_message(msg.chat.id, text=text.onlyadm.format(msg.from_user.id), parse_mode="HTML")
            time.sleep(5)
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.delete_message(msg.chat.id, msg_delete.message_id)


#
#
# New/Left chat members

@bot.message_handler(content_types=["new_chat_members"])
def triggers(msg):
    if not msg.new_chat_member.is_bot == True:
        if msg.chat.id == GROUP_ID:
            try:
                bot.pin_chat_message(GROUP_ID, 2)  # закріпити правила
            except Exception:
                pass
            uid = msg.new_chat_member.id
            keyboard = types.InlineKeyboardMarkup()
            url_button1 = types.InlineKeyboardButton(text="Правила", url="https://t.me/avmafia/34")
            url_button2 = types.InlineKeyboardButton(text="Як грати", url="https://t.me/avmafia/5")
            url_button3 = types.InlineKeyboardButton(text="Інструкція", url="https://t.me/avmafia/2")
            keyboard.add(url_button1, url_button2)
            keyboard.add(url_button3)
            send_message = bot.send_message(msg.chat.id,
                                            text=text.hello.format(uid, msg.new_chat_member.first_name),
                                            parse_mode="HTML", reply_markup=keyboard)
            if not uid in uids:
                cur.execute("INSERT INTO active (uids) VALUES (%s)", [uid])
                cur.execute("INSERT INTO all_uids (list) VALUES (%s)", [uid])
                uids.append(uid)
            ##### Вибрати та видалити id повідомлення
            new_bot_message_id = send_message.message_id
            type_name = 'new_chat_member'
            cur.execute("SELECT id FROM messages WHERE type = %s", [type_name])
            old_bot_message_id = cur.fetchone()
            try:
                bot.delete_message(msg.chat.id, old_bot_message_id)
            except Exception:
                pass
            cur.execute("UPDATE messages SET id = %s WHERE type = %s", [new_bot_message_id, type_name])
            conn.commit()
            ##### Вибрати та видалити id повідомлення
        elif msg.chat.id == GROUP_ID_ACTIVE:
            uid_admin = msg.new_chat_member.id
            if not uid_admins in uids_admins:
                cur.execute("INSERT INTO active_admins (uids_admins) VALUES (%s)", [uid_admin])
                conn.commit()
                uids_admins.append(uid_admin)
        else:
            bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                             parse_mode="HTML")
    else:
        pass


@bot.message_handler(content_types=["left_chat_member"])
def triggers(msg):
    if msg.chat.id == GROUP_ID:
        uid = msg.left_chat_member.id
        if uid in uids:
            cur.execute('DELETE FROM active WHERE uids = %s', [uid])
            cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
            conn.commit()
            uids.remove(uid)
    elif msg.chat.id == GROUP_ID_ACTIVE:
        uid_admin = msg.left_chat_member.id
        if uid_admin in uids_admins:
            cur.execute('DELETE FROM active_admins WHERE uids_admins = %s', [uid_admin])
            conn.commit()
            uids_admins.remove(uid_admin)
    else:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")


#
#
# Commands

@bot.message_handler(commands=['print'])
def triggers(msg):
    message_pin = bot.get_chat(GROUP_ID).pinned_message
    print(message_pin.message_id)


@bot.message_handler(commands=['pin'])
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.pin_chat_message(GROUP_ID, 2)  # закріпити правила
            delete_send_message = bot.send_message(msg.chat.id, text.pinned_terms, disable_web_page_preview=True, parse_mode='HTML')
            time.sleep(5)
            bot.delete_message(msg.chat.id, delete_send_message.message_id)
        except Exception:
            delete_send_message = bot.send_message(msg.chat.id, text.not_pinned_terms, disable_web_page_preview=True, parse_mode='HTML')
            time.sleep(5)
            bot.delete_message(msg.chat.id, delete_send_message.message_id)

@bot.message_handler(content_types=["pinned_message"])
def triggers(msg):
    message_pin = bot.get_chat(GROUP_ID).pinned_message
    if message_pin.message_id == 2:
        bot.delete_message(msg.chat.id, msg.message_id)



@bot.message_handler(commands=['гра'])
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        bot.delete_message(msg.chat.id, msg.message_id)
        next_game_message = bot.send_message(GROUP_ID, text.next_game, parse_mode="HTML")
        bot.pin_chat_message(GROUP_ID, next_game_message.message_id)


@bot.message_handler(commands=['гайд', 'guide'])
def triggers(msg):
    cid = msg.chat.id
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text='Читати правила', url='https://t.me/mafia_pravyla')
    keyboard.add(url_button)
    send_message = bot.send_message(cid, text=text.guide, parse_mode='HTML', reply_markup=keyboard)
    new_bot_message_id = send_message.message_id
    type_name = 'guide'
    ##### Вибрати та видалити id повідомлення
    cur.execute("SELECT id FROM messages WHERE type = %s", [type_name])
    old_bot_message_id = cur.fetchone()
    try:
        bot.delete_message(msg.chat.id, old_bot_message_id)
    except Exception:
        pass
    cur.execute("UPDATE messages SET id = %s WHERE type = %s", [new_bot_message_id, type_name])
    conn.commit()
    ##### Зберегти id поста


# kick ban COMBOT
@bot.message_handler(regexp='!ban|!kick|/ban|/kick')
def triggers(msg):
    if not msg.chat.id == GROUP_ID:
        bot.send_message(msg.chat.id, text.notmafia.format(msg.from_user.id, msg.from_user.first_name),
                         parse_mode="HTML")
    else:
        admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
        if msg.from_user.id in admins:
            uid = msg.reply_to_message.from_user.id
            if uid in uids:
                print(uid)
                cur.execute('DELETE FROM active WHERE uids = %s', [uid])
                cur.execute('DELETE FROM all_uids WHERE list = %s', [uid])
                conn.commit()
                uids.remove(uid)


# Text
step = {}
true = ""


@bot.message_handler(commands=['чат'])
def subscribe_chat(msg):
    if msg.chat.id == GROUP_ID_ACTIVE:
        bot.send_message(GROUP_ID_ACTIVE, "Напиши повідомлення, яке хочеш відправити у чат від імені бота.😁",
                         parse_mode="HTML")
        step[true] = 1
        type_name = 'text_user_id'
        cur.execute("UPDATE messages SET id = %s WHERE type = %s", [msg.from_user.id, type_name])
        conn.commit()
    else:
        pass


@bot.message_handler(func=lambda message: step.get(true) == 1)
def add_user_active(msg):
    if msg.chat.id == GROUP_ID_ACTIVE:
        type_name = 'text_user_id'
        cur.execute("SELECT id FROM messages WHERE type = %s", [type_name])
        text_user_id = cur.fetchone()
        if msg.from_user.id in text_user_id and not msg.text == '!стоп':
            bot.send_message(GROUP_ID, msg.text, parse_mode="HTML")
        else:
            bot.send_message(GROUP_ID_ACTIVE, "Відправка повідомлення скасована...😕", parse_mode="HTML")
        step[true] = 0


# Good Morning
@bot.message_handler(commands=['gm'])
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        bot.delete_message(msg.chat.id, msg.message_id)
        type_name = 'good_morning'
        cur.execute("SELECT id FROM messages WHERE type = %s", [type_name])
        good_morning_value = cur.fetchone()
        if 1 in good_morning_value:
            next_game_message = bot.send_message(GROUP_ID, text.good_morning_1, parse_mode="HTML")
            bot.pin_chat_message(GROUP_ID, next_game_message.message_id)
        elif 0 in good_morning_value:
            next_game_message = bot.send_message(GROUP_ID, text.good_morning_0, parse_mode="HTML")
            bot.pin_chat_message(GROUP_ID, next_game_message.message_id)
    else:
        bot.delete_message(msg.chat.id, msg.message_id)
        delete_send_message = bot.send_message(msg.chat.id, text=text.onlyadm.format(msg.from_user.id),
                                               parse_mode="HTML")
        time.sleep(5)
        bot.delete_message(msg.chat.id, delete_send_message.message_id)


@bot.message_handler(regexp='change_gm')
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        type_name = 'good_morning'
        cur.execute("SELECT id FROM messages WHERE type = %s", [type_name])
        good_morning_value = cur.fetchone()
        if 1 in good_morning_value:
            cur.execute("UPDATE messages SET id = %s WHERE type = %s", [0, type_name])
            bot.send_message(msg.chat.id, text=text.good_morning_change_0, parse_mode="HTML")
        elif 0 in good_morning_value or None in good_morning_value:
            cur.execute("UPDATE messages SET id = %s WHERE type = %s", [1, type_name])
            bot.send_message(msg.chat.id, text=text.good_morning_change_1, parse_mode="HTML")
        conn.commit()
    else:
        bot.delete_message(msg.chat.id, msg.message_id)
        delete_send_message = bot.send_message(msg.chat.id, text=text.onlyadm.format(msg.from_user.id),
                                               parse_mode="HTML")
        time.sleep(5)
        bot.delete_message(msg.chat.id, delete_send_message.message_id)


@bot.message_handler(regexp='set_gm')
def triggers(msg):
    admins = [admin.user.id for admin in bot.get_chat_administrators(GROUP_ID)]
    if msg.from_user.id in admins:
        type_name = 'good_morning_set'
        cur.execute("SELECT id FROM messages WHERE type = %s", [type_name])
        good_morning_value = cur.fetchone()
        if 1 in good_morning_value:
            cur.execute("UPDATE messages SET id = %s WHERE type = %s", [0, type_name])
            bot.send_message(msg.chat.id, text=text.good_morning_off, parse_mode="HTML")
        elif 0 in good_morning_value or None in good_morning_value:
            cur.execute("UPDATE messages SET id = %s WHERE type = %s", [1, type_name])
            bot.send_message(msg.chat.id, text=text.good_morning_on, parse_mode="HTML")
        conn.commit()
    else:
        bot.delete_message(msg.chat.id, msg.message_id)
        delete_send_message = bot.send_message(msg.chat.id, text=text.onlyadm.format(msg.from_user.id),
                                               parse_mode="HTML")
        time.sleep(5)
        bot.delete_message(msg.chat.id, delete_send_message.message_id)


# Auto Good Morning of 06:56 & pin message of guide
def job():
    type_name = 'good_morning'
    type_name2 = 'good_morning_set'
    cur.execute("SELECT id FROM messages WHERE type = %s", [type_name])
    good_morning_value1 = cur.fetchone()
    cur.execute("SELECT id FROM messages WHERE type = %s", [type_name2])
    good_morning_value2 = cur.fetchone()
    if 1 in good_morning_value2:
        if 1 in good_morning_value1:
            next_game_message = bot.send_message(GROUP_ID, text.good_morning_1, parse_mode="HTML")
            bot.pin_chat_message(GROUP_ID, next_game_message.message_id)
        elif 0 in good_morning_value1:
            next_game_message = bot.send_message(GROUP_ID, text.good_morning_0, parse_mode="HTML")
    else:
        pass

def job2():
    try:
        bot.pin_chat_message(GROUP_ID, 2)  # закріпити правила
    except Exception:
        pass


schedule.every().day.at("04:56").do(job)
schedule.every().day.at("10:06").do(job2)

# schedule.every(5).seconds.do(job2)

def go():
    while 1:
        schedule.run_pending()
        time.sleep(1)

t = threading.Thread(target=go, name="test")
t.start()


# Test of bot

@bot.message_handler(regexp='test')
def triggers(msg):
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.send_message(GROUP_ID, text.test_bot, parse_mode="HTML")
    print(text.test_bot)


bot.polling(none_stop=True)