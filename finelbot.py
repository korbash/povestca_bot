#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import os
import io
import logging
from re import U
import re
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PollAnswerHandler,
    filters,
)
import dotenv
from lib.case import case, add_user, connect_to_mongo

dotenv.load_dotenv('keys/keys.env')
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__name__)

SET_town, NEW_CASE, QUESTIONS = range(3)


async def ask_about_town(bot, id):
    await bot.send_message(chat_id=id, text="В каком городе ты живёшь?")
    return


async def ask_more_info(bot, id, open, carrent):
    if len(open) == 0:
        still = 'можешь добавить ещё одно фото/коментарий'
    else:
        still = 'осталось добавить: ' + ', '.join(open)
    await bot.send_message(chat_id=id,
                           text=carrent + ' принял, ' + still +
                           '\nили отправить как есть /send')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Привет! я бот для сбора инфы где и как сейчас вручают повестки.'
        'все собранные данные я выкладываю на онлайн карту, поэтому очень важно чтобы ты прислал точку,'
        'где ты увидел чтото подозрительное.')
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['que'] = None
    await ask_about_town(context.bot, update.effective_chat.id)
    return SET_town


async def set_town(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Отлично теперь можешь рассказывать всё что увидел. '
        'Пиши мне, Присылай фото (они особенно ценятся), и обязательно геолокацию\n'
        'в каком порядке неважно')
    id = update.effective_chat.id
    add_user(update.effective_chat.id, town=update.message.text)
    context.user_data['case'] = case(id)
    return NEW_CASE


async def add_coment(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> int:
    c = context.user_data['case']
    c.add_comment(update.message.text)
    await ask_more_info(context.bot, update.effective_chat.id, c.open_position,
                        c.carrent)
    return NEW_CASE


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo_file = await update.message.photo[-1].get_file()
    data = io.BytesIO()
    await photo_file.download(out=data)
    c = context.user_data['case']
    c.add_foto(data)
    await ask_more_info(context.bot, update.effective_chat.id, c.open_position,
                        c.carrent)
    return NEW_CASE


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    loc = update.message.location
    c = context.user_data['case']
    c.add_gps(loc.latitude, loc.longitude)
    await ask_more_info(context.bot, update.effective_chat.id, c.open_position,
                        c.carrent)
    return NEW_CASE


async def ask_questions(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    c = context.user_data['case']
    id = c.user_id
    if context.user_data['que'] is not None:
        c.add_ans(update.poll_answer.option_ids)
    try:
        que, ans, opt = next(c.question)
        await context.bot.send_poll(id, que, ans, is_anonymous=False, **opt)
        context.user_data['que'] = que
        return QUESTIONS
    except StopIteration:
        await context.bot.send_message(chat_id=id,
                                       text='отлично! отправил случай в базу, '
                                       'готов записывать новый кейс. '
                                       'Присылай фото, геолокацию')
        del c
        context.user_data['case'] = case(id)
        context.user_data['que'] = None
        return NEW_CASE


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ['tg_token']).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SET_town: [MessageHandler(filters.TEXT, set_town)],
            NEW_CASE: [
                MessageHandler(filters.PHOTO, photo),
                MessageHandler(filters.LOCATION, location),
                MessageHandler(filters.TEXT & (~filters.COMMAND), add_coment),
                CommandHandler('send', ask_questions)
            ],
            QUESTIONS: [PollAnswerHandler(ask_questions)]
        },
        fallbacks=[CommandHandler("restart", start)],
        per_chat=False)

    application.add_handler(conv_handler)

    connect_to_mongo()
    application.run_polling()


if __name__ == "__main__":
    main()