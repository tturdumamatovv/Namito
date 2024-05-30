import requests
import uuid
import random
import telegram

from django.conf import settings
from asgiref.sync import sync_to_async

from xml.etree import ElementTree as ET
from decouple import config


# TELEGRAM_BOT_TOKEN = '7441310771:AAHicm83gxd6F5E9hpIXjwNQ7551ZeA6PnU'


def generate_confirmation_code():
    confirmation_code = ''.join(random.choices('0123456789', k=4))
    print(confirmation_code)
    return confirmation_code


def send_sms(phone_number, confirmation_code):
    login = config('login_nikita')
    password = config('password_nikita')
    transaction_id = str(uuid.uuid4())
    sender = config('sender_nikita')
    text = f'Your confirmation code id: {confirmation_code}'

    request_body = ET.Element("message")
    ET.SubElement(request_body, "login").text = login
    ET.SubElement(request_body, "pwd").text = password
    ET.SubElement(request_body, "id").text = transaction_id
    ET.SubElement(request_body, "sender").text = sender
    message_send = f"Ваш код подтверждения: {confirmation_code}"
    ET.SubElement(request_body, "text").text = message_send
    phones_element = ET.SubElement(request_body, "phones")
    ET.SubElement(phones_element, "phone").text = phone_number

    if settings.PRODUCTION:
        ET.SubElement(request_body, "test").text = "0"

    request_body_str = ET.tostring(request_body, encoding="UTF-8", method="xml")

    url = 'https://smspro.nikita.kg/api/message'
    headers = {'Content-Type': 'application/xml'}

    response = requests.post(url, data=request_body_str, headers=headers)
    if response.status_code == 200:
        print(response.content)
        print('SMS sent successfully')
    else:
        print('Failed to send SMS')


# async def get_chat_id_for_phone(phone_number):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         for update in data['result']:
#             if 'message' in update and 'contact' in update['message']:
#                 if update['message']['contact']['phone_number'] == phone_number:
#                     return update['message']['chat']['id']
#     return None



# async def send_telegram_message(chat_id, otp_code):
#     bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
#     message = f"Ваш код подтверждения: {otp_code}"
#     await bot.send_message(chat_id=chat_id, text=message)
