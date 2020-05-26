from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from connector import get_forecast


def handle_inline_key(query, bot, iterable, text):
    delete_inline_key(query, bot)
    keyboard = [[InlineKeyboardButton(i, callback_data=i)] for i in iterable]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(text=text, chat_id=query.message.chat.id, reply_markup=reply_markup)


def delete_inline_key(query, bot):
    query.answer()
    chat_id, message_id = query.message.chat.id, query.message.message_id
    bot.delete_message(chat_id=chat_id, message_id=message_id)


def start_conv(message, iterable):
    keyboard = [[InlineKeyboardButton(i, callback_data=i) for i in iterable]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply_text('En que linea vas a viajar?', reply_markup=reply_markup)


def get_subway_eta(data):
    return get_forecast(data)
