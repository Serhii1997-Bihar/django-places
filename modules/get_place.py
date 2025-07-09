import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models import LinksModel, PlaceModel
from additional.selenium_launcher import SeleniumDriver
from additional.company_info import GoogleMapsScraper
from additional.about import AboutCollector
from mongoengine import connect
import re

connect(db='places_db', host='localhost', port=27017)

pattern = r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)"

def clean_int(value):
    try:
        cleaned = re.sub(r'[^\d]', '', str(value))
        return int(cleaned) if cleaned else 0
    except Exception:
        return 0

def process_places_for_user(user):
    driver = SeleniumDriver()
    scraper = GoogleMapsScraper(driver.get_driver())
    about_collector = AboutCollector(driver.get_driver())

    try:
        pending_links = LinksModel.objects(status='Pending', user=user)
        for item in pending_links:
            print(f'\n🔗 Обробка: {item.link}')
            driver.load_url(item.link)

            try:
                overview = scraper.get_overview()
                about_info = about_collector.collect_about()
            except Exception as e:
                print(f"❌ Помилка при зборі даних: {e}")
                continue

            latitude, longitude = None, None
            match = re.search(pattern, item.link)
            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))

            existing = PlaceModel.objects(link=item.link, user=user).first()
            if existing:
                print("⚠️ Вже існує:", existing.name)
            else:
                if not isinstance(about_info, dict):
                    about_info = {}

                open_hours = overview.get('open_hours') or {}
                open_24_7 = overview.get('open_24_7') or {}
                image_url = overview.get('image') if isinstance(overview.get('image'), str) else None

                place = PlaceModel(
                    link=item.link,
                    category=item.category,
                    name=overview.get('name'),
                    rating=overview.get('rating'),
                    num_reviews=clean_int(overview.get('num_reviews')),
                    about=about_info,
                    full_address=overview.get('full_address'),
                    country=overview.get('country'),
                    city=overview.get('city'),
                    state=overview.get('state'),
                    zip_code=overview.get('zip_code'),
                    address=overview.get('address'),
                    located_in=overview.get('located_in'),
                    lat=latitude,
                    image=image_url,
                    lng=longitude,
                    place_type=overview.get('place_type'),
                    open_hours=open_hours if isinstance(open_hours, dict) else {},
                    open_24_7=open_24_7 if isinstance(open_24_7, dict) else {},
                    phone=overview.get('phone'),
                    website=overview.get('website'),
                    user=user,  # додано user
                )
                place.save()
                print(f"✅ Додано: {place.name}")

            item.status = 'Done'
            item.save()

    finally:
        driver.quit()
        print("✅ Драйвер завершив роботу")
