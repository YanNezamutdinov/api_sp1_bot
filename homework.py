import os
import requests
import telegram
import time
from dotenv import load_dotenv
import logging

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    
    if 'homework_name' and 'status' in homework:
        homework_name = homework.get('homework_name')
        status = homework.get('status')
        if status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif status == 'approved':
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        else:
            return f'Прилетел странный статус! status = {status}'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    return "Oops! homework_name or status not found!"


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, params=params, headers=headers)
    except Exception as e:
        logging.info(f'Oops! Error: {e}')
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    bot.send_message(chat_id=CHAT_ID, text=f'praktikum-status запущен! {current_timestamp}')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()