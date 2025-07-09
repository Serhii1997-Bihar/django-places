import sys
import os
import time
import re
import requests
from urllib.parse import urlparse
from concurrent import futures

# Додаємо корінь проєкту до PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mongoengine import connect
from models import PlaceModel  # твоя модель MongoEngine
from additional.emails_by_popular import EmailExtractor
from additional.emails_mailto import MailtoEmailExtractor
from additional.emails_corpmail import CorpEmailExtractor
from additional.social import SocialLinksExtractor
from additional.email_domains import top_email_domains

# Налаштування MongoDB
connect(db='exchanger_db', host='localhost', port=27017)

# Заголовки для запитів
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

# Ініціалізація екстракторів
email_extractor = EmailExtractor(top_email_domains)
social_extractor = SocialLinksExtractor(headers)


def load_page_with_retries(url, retries=2, delay=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"[{url}] Спроба {attempt + 1}/{retries} не вдалася: {e}")
            time.sleep(delay)
    return None


def process_item(item: PlaceModel):
    if not item.website:
        item.status = 'Done'
        item.save()
        return

    print(f"\n🔍 Обробка: {item.website}")
    response = load_page_with_retries(item.website)

    if response is None:
        item.status = 'LoadError'
        item.save()
        return

    html = response.text
    emails = email_extractor.extract(html)

    if not emails:
        emails = MailtoEmailExtractor(html).find_emails()

    if not emails:
        emails = CorpEmailExtractor(html).find_corp_emails(item.website)

    item.email = emails if emails else None
    print(f"📧 Знайдено email: {emails}")

    # Соціальні мережі
    social_links = social_extractor.extract_links(item.website)
    item.instagram = social_links.get('instagram')
    item.facebook = social_links.get('facebook')
    item.twitter = social_links.get('twitter')
    item.linkedin = social_links.get('linkedin')
    item.youtube = social_links.get('youtube')

    print(f"🔗 Соціальні мережі: {social_links}")
    item.status = 'Done'
    item.save()

items = PlaceModel.objects()

# Багатопотокова обробка
with futures.ThreadPoolExecutor(max_workers=40) as executor:
    executor.map(process_item, items)

print("✅ Усі елементи оброблено.")
