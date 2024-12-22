import telebot
from telebot import types
import json
import os


bot = telebot.TeleBot(os.getenv("TOKEN"))

ADMIN_ID = os.getenv("ADMIN_ID")

@bot.message_handler(commands=['start'])
def start(message):
    global USER_NAME
    USER_NAME = message.from_user.first_name
    global USER_ID
    USER_ID = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Перейти на сайт', web_app=types.WebAppInfo(url='https://nyam-kohl.vercel.app/')))
    bot.send_message(USER_ID, f'Привет, {USER_NAME}!\nЖду твоего заказа)', reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def web_app_data_handler(message):
    try:
        data = json.loads(message.web_app_data.data)
        global order
        order = data.get("order", [])
        total_price = data.get("total_price", 0)

        global order_details
        order_details = "\n".join([
            f"{item['name']} - {item['quantity']} шт. — {item['total_price']} ₽"
            for item in order
        ])
        admin_response = (
            f"Вам поступил заказ от {USER_NAME}:\n\n"
            f"{order_details}\n\n"
            f"Итого: {total_price} ₽"
        )
        response = (    
            f"Ваш заказ:\n\n"
            f"{order_details}\n\n"
            f"Итого: {total_price} ₽"
        )

        remove_keyboard = types.ReplyKeyboardRemove()
        bot.send_message(ADMIN_ID, admin_response, reply_markup=remove_keyboard)
        bot.send_message(USER_ID, response)

        bot.send_message(USER_ID, "✅ Ваш заказ успешно отправлен! Вы получите уведомление, когда заказ начнет выполняться")

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Да', callback_data="yes")
        btn2 = types.InlineKeyboardButton('Нет', callback_data="no")
        markup.row(btn1, btn2)

        bot.send_message(ADMIN_ID, "❓ Вы готовы к выполнению заказа?", reply_markup=markup)

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка обработки данных: {str(e)}")
        bot.send_message(USER_ID, "❌ Возникла ошибка, попробуйте снова через пару минут")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global order
    global items_markup

    if call.data == "yes":
        bot.delete_message(ADMIN_ID, call.message.message_id)
        bot.delete_message(USER_ID, call.message.message_id-1)
        items_markup = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(f'{item["name"]} — {item["quantity"]} шт.', callback_data=f'item_{item["name"]}')
            for item in order
        ]
        for i in range(0, len(buttons), 2):
            items_markup.row(*buttons[i:i+2])

        bot.send_message(USER_ID, "✅ Ваш заказ выполняется! По готовности блюд Вы будете получать уведомления")
        bot.send_message(ADMIN_ID, "❓ Выберите блюдо", reply_markup=items_markup)
        

    if call.data == "no":
        bot.delete_message(ADMIN_ID, call.message.message_id)
        timeout_markup = types.InlineKeyboardMarkup()
        timeout_markup.add(types.InlineKeyboardButton('🔪 Приступить к выполнению заказа', callback_data="yes"))
        bot.send_message(ADMIN_ID, '❌ Вы отложили заказ', reply_markup=timeout_markup)
        bot.send_message(USER_ID, "❌ Ваш заказ отложен")

    if call.data.startswith("item_"):
        item_name = call.data.split("_", 1)[1]
        item = next((item for item in order if item["name"] == item_name), None)

        if item:
            bot.delete_message(ADMIN_ID, call.message.message_id)
            bot.delete_message(USER_ID, call.message.message_id-1)
            time_markup = types.InlineKeyboardMarkup()
            time_markup.add(types.InlineKeyboardButton("✅ Блюдо готово!", callback_data=f"done_{item_name}"))
            bot.send_message(USER_ID, f'🔪 Блюдо "{item["name"]} — {item["quantity"]} шт." готовится! По готовности Вам придет уведомление')
            bot.send_message(ADMIN_ID, f"🔪 Вы готовите '{item['name']} — {item['quantity']} шт.'", reply_markup=time_markup)


    if call.data.startswith("done_"):
        item_name = call.data.split("_", 1)[1]

        order = [item for item in order if item["name"] != item_name]

        bot.send_message(USER_ID, f'✅ Блюдо "{item_name}" готово! О готовности других блюд Вам придут уведомления')
        bot.delete_message(ADMIN_ID, call.message.message_id)
        bot.delete_message(USER_ID, call.message.message_id-1)

        if order:
            items_markup = types.InlineKeyboardMarkup()
            buttons = [
                types.InlineKeyboardButton(f'{item["name"]} — {item["quantity"]} шт.', callback_data=f'item_{item["name"]}')
                for item in order
            ]
            for i in range(0, len(buttons), 2):
                items_markup.row(*buttons[i:i+2])

            bot.send_message(ADMIN_ID, "❓ Выберите блюдо", reply_markup=items_markup)
        else:
            bot.delete_message(USER_ID, call.message.message_id+1)
            bot.send_message(USER_ID, "✅ Все блюда приготовлены! Приятного аппетита)")
            bot.send_message(ADMIN_ID, "✅ Все блюда приготовлены!")



bot.polling(none_stop=True) 