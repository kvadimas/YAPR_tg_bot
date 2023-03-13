import datetime as DT
import logging
import os
import time
from http import HTTPStatus

import requests

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

from exceptions import TokensErrorException
from homework import *
import telegram

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_BOT_KVADIMAS_TOKEN = os.getenv('TELEGRAM_BOT_KVADIMAS_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
# ОТЛАДКА.
time_test = int(DT.datetime.strptime(
    '2023-01-01 04:00:00',
    '%Y-%m-%d %H:%M:%S'
).timestamp())
# timestamp = time_test

# Глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.DEBUG,
    filename='mane.log',
    filemode='a',
    format='%(asctime)s, %(funcName)s, %(levelname)s, %(message)s'
)

# А тут установлены настройки логгера для текущего файла
logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл
logger.setLevel(logging.INFO)
# Указываем обработчик логов
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)

def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Отправлено сообщение в тг.')
    except Exception:
        logging.error('Ошибка отправки сообщения в тг.')


def main():
    """
    Основная логика работы бота.
    1. Сделать запрос к API.
    2. Проверить ответ.
    3. Если есть обновления — получить статус работы из обновления и отправить
    сообщение в Telegram.
    4. Подождать некоторое время и вернуться в пункт 1.
    """
    logging.debug('Проверка доступности переменных окружения.')
    check_tokens()
    logging.debug('Переменное окружение: Ok.')
    logging.debug('Запуск бота.')
    bot = telegram.Bot(token=TELEGRAM_BOT_KVADIMAS_TOKEN)
    bot.send_message(TELEGRAM_CHAT_ID, 'Hello!')
    timestamp = 0
    status = ''
    while True:
        try:
            logging.debug('Запрос к эндпоинту API-ЯП.')
            response = get_api_answer(timestamp)
            logging.debug('Проверка ответа API.')
            checked_hwk = check_response(response)
            logging.debug('Проверка ответа API: OK')
            if len(checked_hwk) == 0:
                continue
            elif len(checked_hwk) > 1:
                homework = checked_hwk['homeworks'][0]
            else:
                homework = checked_hwk
            if homework.get('status') != status:
                message = parse_status(homework)
                logging.debug(homework)
                logging.info(message)
                send_message(bot, message=message)
                status = homework['status']
                timestamp = int(DT.datetime.strptime(
                    homework['date_updated'],
                    '%Y-%m-%dT%H:%M:%SZ'
                ).timestamp())
                logging.debug(f'Время запроса: {timestamp}')
            else:
                logging.info('Нет новых статусов.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.info(message)
            send_message(bot, message)
        finally:
            logging.debug(f'Засыпаю на {RETRY_PERIOD}c')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
