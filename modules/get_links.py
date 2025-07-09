import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


from models import LinksModel, UserModel
from additional.search_companies import GoogleMapsScraper


def run_parsing(country, city, category, user):
    link = f'https://www.google.com.ua/maps/search/{country}+{city}+{category}/?hl=en'
    scraper = GoogleMapsScraper()
    response = scraper.scrape_link(link)
    count = 0

    for name, link in response.items():
        if not LinksModel.objects(link=link).first():
            new_link = LinksModel(
                user=user,
                link=link,
                name=name,
                country=country,
                city=city,
                category=category,
                status='Pending'
            )
            new_link.save()
            count += 1
            print(f"[+] Added: {name} | {link}")
        else:
            print(f"[-] Exists: {link}")

    print(f"✅ Added {count} new links from {len(response)} scraped links")
