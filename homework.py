import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)s',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)s'
)
handler.setFormatter(formatter)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Сообщение в чат {TELEGRAM_CHAT_ID}: {message}')
    except Exception as error:
        logger.error(f'Ошибка отправки сообщения: {error}')


def get_api_answer(current_timestamp):
    """
    Делает запрос к API.
    Возвращает ответ, преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        raise Exception(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        status_code = response.status_code
        logging.error(f'Ошибка {status_code}')
        raise Exception(f'Ошибка {status_code}')
    return response.json()


def check_response(response):
    """Получаем список домашних работ."""
    response = response['homeworks']
    if response is None:
        raise Exception('Ошибка словарь homeworks пустой')
    if isinstance(response, dict):
        raise Exception('Ошибка homeworks не словарь')
    return response[0]


def parse_status(homework):
    """Возвращает статус конкретной домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('homework_name отсутствует в homework')
    if 'status' not in homework:
        raise KeyError('status отсутствует в homework')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise Exception('Неизвестный статус домашей работы')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    else:
        logging.critical('Отсутствует обязательная переменная окружения')
        return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    STATUS = ''
    ERROR = ''
    if check_tokens() is False:
        raise Exception('Отсутствует обязательная переменная окружения')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            message = parse_status(check_response(response))
            if message != STATUS:
                send_message(bot, message)
                STATUS = message
            time.sleep(RETRY_TIME)

        except Exception as error:
            logging.error(f'Ошибка при отправке сообщения: {error}')
            message = f'Сбой в работе программы: {error}'
            if message != ERROR:
                send_message(bot, message)
                ERROR = message
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
