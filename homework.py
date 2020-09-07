import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.environ("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.environ('TELEGRAM_TOKEN')
CHAT_ID = os.environ('TELEGRAM_CHAT_ID')
PRACTICUM_URI = os.environ('PRACTICUM_URI')
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(PRACTICUM_URI, params=params, headers=headers)
    print(homework_statuses.json())
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id = CHAT_ID, text = message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    bot.send_message(chat_id = CHAT_ID, text = f'praktikum-status запущен! {current_timestamp}')

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