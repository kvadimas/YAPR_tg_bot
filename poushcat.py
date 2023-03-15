import logging

import requests

from telegram import ReplyKeyboardMarkup


# Локальный логер
logger = logging.getLogger(__name__)


URL = 'https://api.thecatapi.com/v1/images/search'


def get_new_image():
    try:
        response = requests.get(URL)
    except Exception as error:
        # Печатать информацию в консоль теперь не нужно:
        # всё необходимое будет в логах
        # print(error)
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/cat'],['/homework']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=(f'Привет, {name}. Я умею присылать котиков по запросу и отправлять статус домашнего задания.',),
        reply_markup=button
    )



if __name__ == '__main__':
    main() 