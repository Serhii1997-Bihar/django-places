import requests
from django.conf import settings
from io import BytesIO

def send_message(chat_id, image_bytes, caption):
    try:
        token = settings.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{token}/sendPhoto"

        files = {
            'photo': ('photo.jpg', BytesIO(image_bytes))
        }
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': 'HTML',
        }

        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        result = response.json()

        if not result.get('ok', False):
            print(f"❌ Error {result.get('error_code')}: {result.get('description')}")
    except requests.RequestException as e:
        print(f"Telegram error: {e}")