import logging
import os
from telegram.ext import MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from schema import lines_stops, lines_directions
from utils import handle_inline_key, start_conv, get_subway_eta, delete_inline_key

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
subway_api_information = {}


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="A partir de ahora podemos hablar!")


def next_subway(update, context):
    start_conv(update.message, lines_stops)
    return 'station'


def station(update, context):
    global subway_api_information
    query, bot = update.callback_query, context.bot
    handle_inline_key(query, bot, lines_stops[query.data], 'En que estacion vas a subir?')
    subway_api_information['line'] = query.data
    return 'direction'


def direction(update, context):
    global subway_api_information
    query, bot = update.callback_query, context.bot
    handle_inline_key(query, bot, lines_directions[subway_api_information['line']], 'Hacia donde vas?')
    subway_api_information['station'] = query.data
    return 'eta'


def subway_eta(update, context):
    global subway_api_information
    query, bot = update.callback_query, context.bot
    subway_api_information['direction'] = query.data
    delete_inline_key(query, bot)
    text = get_subway_eta(subway_api_information)
    bot.send_message(text=text, chat_id=query.message.chat.id)
    return


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Todavia no se como hacer eso... Intenta con otra cosa!")


def error(update, context):
    logger.error(f'{update} caused error {context.error}')
    context.bot.send_message(chat_id=context.callback_query.message.chat.id,
                             text='Ups! Ocurrio un error, intenta de nuevo!')


def main():
    updater = Updater(token=os.environ['BOT_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('subte', next_subway)],
        states={
            'station': [CallbackQueryHandler(station)],
            'direction': [CallbackQueryHandler(direction)],
            'eta': [CallbackQueryHandler(subway_eta)]
        },
        fallbacks=[CommandHandler('subte', next_subway)]
    )
    dispatcher.add_handler(conv_handler)

    dispatcher.add_error_handler(error)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
