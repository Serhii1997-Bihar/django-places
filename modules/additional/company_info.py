# scraper.py

from time import sleep
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from unidecode import unidecode
import re, time
from .selenium_launcher import SeleniumDriver

class GoogleMapsScraper:
    def __init__(self, driver:SeleniumDriver):
        """Initialize the scraper with the Selenium driver."""
        self.driver:SeleniumDriver = driver
        self.wait = WebDriverWait(self.driver, 5)

    def get_name(self):
        """Extract the name of the place."""
        try:
            return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))).text.strip()
        except NoSuchElementException:
            return None

    def get_address_components(self):
        """Extract address components from the page."""
        try:
            full_address = self.driver.find_element(By.XPATH, "//button[@data-item-id='address']").get_attribute('aria-label').replace('Address: ', '').strip()
            address_parts = full_address.split(',')
            address = address_parts[0]
            country = address_parts[-1].strip()
            
            state_zip = address_parts[-2].strip()
            city = address_parts[-3].strip()
            state_zip_res:list = state_zip.split(' ')

            zip_code = state_zip_res.pop(-1)
            state = state_zip_res.pop(-1)

            # city = ' '.join(state_zip_res)

            return full_address, address, country, city, state, zip_code
        except (NoSuchElementException, IndexError, ValueError):
            return None, None, None, None, None, None  
         
    def get_located_in(self):
        """Extract information about the place's location context."""
        try:
            return self.driver.find_element(By.XPATH, "//div[contains(text(), 'Located in:')]").text.replace('Located in: ', '').strip()
        except NoSuchElementException:
            return None

    def get_phone(self):
        """Extract the phone number of the place."""
        try:
            return self.driver.find_element(By.XPATH, "//button[contains(@data-item-id, 'phone:tel')]").get_attribute('data-item-id').replace('phone:tel:', '').strip()
        except NoSuchElementException:
            return None

    def get_image(self):
        """Extract the phone number of the place."""
        try:
            return self.driver.find_element(By.XPATH, "//button[@class='aoRNLd kn2E5e NMjTrf lvtCsd ']").find_element(By.TAG_NAME, "img").get_attribute("src")
        except NoSuchElementException:
            return None

    def get_website(self):
        """Extract the website link of the place."""
        try:
            return self.driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Website:')]").get_attribute('href')
        except NoSuchElementException:
            return None

    def get_clinic_type(self):
        """Extract the type of the clinic."""
        try:
            return self.driver.find_element(By.XPATH, "//button[@class='DkEaL ']").text.strip()
        except NoSuchElementException:
            return None

    def get_rating(self):
        """Extract the rating of the place."""
        try:
            return self.driver.find_element(By.XPATH, "//div[@class='fontDisplayLarge']").get_attribute('innerHTML')
        except NoSuchElementException:
            return None

    def get_num_reviews(self):
        """Extract the number of reviews."""
        try:
            return self.driver.find_element(By.XPATH, "//span[contains(@aria-label, 'reviews')]").text.replace('(', '').replace(')', '').strip()
        except NoSuchElementException:
            return None

    def get_open_hours(self):
        """Extract open hours and check if the place is open 24/7."""

        # Проверяем 24/7
        try:
            find_24_7 = self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='ZDu9vd']"))).text.strip()
            open_24_7 = 'Yes' if find_24_7 == 'Open 24 hours' else 'No'
        except TimeoutException:
            open_24_7 = 'No'

        # Парсим таблицу с часами работы
        open_hours = {}
        try:
            table_open_hours = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.eK4R0e.fontBodyMedium")))
            rows_open_hours = table_open_hours.find_elements(By.CSS_SELECTOR, "tr.y0skZc")

            for row in rows_open_hours:
                try:
                    # Достаём значение из data-value
                    button = row.find_element(By.CSS_SELECTOR, "td.HuudEc button")
                    data_value = button.get_attribute("data-value")  # Например: "Monday, 9 AM–4 PM"

                    # Разбираем строку на день недели и время
                    if data_value:
                        day, hours = data_value.split(", ", 1)
                        open_hours[day] = unidecode(hours.strip())
                        
                except NoSuchElementException:
                    continue  # Пропускаем строки, если что-то не найдено

        except TimeoutException:
            open_hours = {}

        return open_hours, open_24_7

    def get_overview(self):
        print('Start scraping overview')
        overview = {}
        overview['name'] = self.get_name()
        overview['full_address'], overview['address'], overview['country'], overview['city'], overview['state'], overview['zip_code'] = self.get_address_components()
        overview['located_in'] = self.get_located_in()
        overview['phone'] = self.get_phone()
        overview['website'] = self.get_website()
        overview['place_type'] = self.get_clinic_type()
        overview['rating'] = self.get_rating()
        overview['num_reviews'] = self.get_num_reviews()
        overview['open_hours'], overview['open_24_7'] = self.get_open_hours()
        overview['image'] = self.get_image()
        
        print('Overview done')
        return overview

    def close(self):
        """Close the Selenium driver."""
        self.driver.quit()


# Отдельный тест класса
if __name__ == "__main__":
    print("Starting tests for GoogleMapsScraper...\n")

    try:
        driver = SeleniumDriver()
        scraper = GoogleMapsScraper(driver.get_driver())

        url = 'https://www.google.com.ua/maps/place/The+Mountain+Bar+%26+Grill/data=!4m7!3m6!1s0x4d334cc8f06757a1:0xb45a74fc6c011a9b!8m2!3d44.814784!4d-83.3590057!16s%2Fg%2F1tj9bmwj!19sChIJoVdn8MhMM00RmxoBbPx0WrQ?authuser=0&hl=en&rclk=1'
        driver.load_url(url)
        print(f'Url - {url}')

        overview = scraper.get_overview()

        pattern = r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)"
        match = re.search(pattern, url)
        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
        
        for item in overview.items():
            print(item)
        print(latitude, longitude)

        scraper.close()
        print("\nAll tests completed.")

    except Exception as e:
        print(e)