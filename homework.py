import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv
from exceptions import APIRequestError, StatusCode

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

VERDICT = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Сообщение в чат {TELEGRAM_CHAT_ID}: {message}')
    except telegram.TelegramError:
        logging.error('Ошибка отправки сообщения', exc_info=True)


def get_api_answer(current_timestamp):
    """
    Делает запрос к API.
    Возвращает ответ, преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as error:
        logging.error(
            f'Ошибка при запросе к основному API: {error}.'
            f'Endpoint={ENDPOINT}, headers={HEADERS}, params={params}',
            exc_info=True
        )
        raise APIRequestError(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        status_code = response.status_code
        logging.error(f'Ошибка {status_code}', exc_info=True)
        raise StatusCode(f'Ошибка {status_code}')
    return response.json()


def check_response(response):
    """Получаем список домашних работ."""
    if type(response) is not dict:
        raise TypeError(f'{response} отличен от словаря')
    if response is None:
        raise Exception('Ошибка словарь homeworks пустой')
    return response['homeworks'][0]


def parse_status(homework):
    """Возвращает статус конкретной домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('homework_name отсутствует в homework')
    homework_status = homework['status']
    if homework_status not in VERDICT:
        raise Exception('Неизвестный статус домашей работы')
    verdict = VERDICT[homework_status]
    return f'Изменился статус проверки работы "{homework["homework_name"]}".' \
           f'{verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    if all(variables) and None not in variables.values():
        return True
    else:
        for variable in variables:
            if variables[variable] is False or variables[variable] is None:
                logging.critical(
                    f'Отсутствует {variable} переменная окружения'
                )
        return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit('Отсутствует обязательная переменная окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    status = ''
    error_bot = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            message = parse_status(check_response(response))
            if message != status:
                send_message(bot, message)
                status = message
            time.sleep(RETRY_TIME)

        except telegram.TelegramError:
            logging.error('Ошибка отправки сообщения')
            time.sleep(RETRY_TIME)

        except APIRequestError as error:
            logging.error(f'Ошибка при запросе к основному API: {error}')
            message = f'Сбой при запросе к основному API: {error}'
            if message != error_bot:
                send_message(bot, message)
                error_bot = message
            time.sleep(RETRY_TIME)

        except Exception as error:
            logging.error(f'Ошибка при отправке сообщения: {error}')
            message = f'Сбой в работе программы: {error}'
            if message != error_bot:
                send_message(bot, message)
                error_bot = message
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
