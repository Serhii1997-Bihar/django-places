from time import sleep
from selenium.webdriver.common.by import By
from .selenium_launcher import SeleniumDriver

class GoogleMapsScraper:
    def __init__(self, headless: bool = True):
        """Initialize the scraper with a Selenium driver."""
        self.selenium_driver = SeleniumDriver(headless)
        self.driver = self.selenium_driver.get_driver()

    def scrape_link(self, url):
        """Scrape a single link and return the name and URL."""
        print("Scraping link:", url)
        self.driver.get(url)
        sleep(2)  # Даем время для загрузки страницы

        last_count = 0
        max_attempts = 20  # Количество проверок перед завершением
        attempts = 0

        while True:
            links_list = self.driver.find_elements(By.XPATH, "//a[@class='hfpxzc']")
            
            if not links_list:
                print("No links found, exiting...")
                break
            
            # Скроллим к последнему элементу
            self.driver.execute_script("arguments[0].scrollIntoView();", links_list[-1])
            print(f'Scrolled: {len(links_list)} items')


            if "You've reached the end of the list" in self.driver.page_source:
                print("You've reached the end of the list")
                break
            sleep(2)  # Даем время на подгрузку новых элементов

            # Проверяем, изменилось ли количество элементов
            if len(links_list) == last_count:
                attempts += 1
                print(f"No new elements found ({attempts}/{max_attempts})")
                if attempts >= max_attempts:
                    print("Reached max attempts. Exiting scroll loop.")
                    break
            else:
                attempts = 0  # Сбрасываем счетчик
                last_count = len(links_list)

        # Снова получаем актуальный список элементов после всех скроллов
        links_list = self.driver.find_elements(By.XPATH, "//a[@class='hfpxzc']")

        company = {}

        for link_element in links_list:
            link = link_element.get_attribute("href")
            name = link_element.get_attribute("aria-label")

            if link and name:
                company[name] = link

        return company

    def close(self):
        """Close the Selenium driver."""
        self.selenium_driver.quit()


# Тестирование класса
if __name__ == "__main__":
    print("Starting tests for GoogleMapsScraper...\n")

    try:
        item = GoogleMapsScraper()

        url = 'https://www.google.com.ua/maps/search/bookkeeping+near+3114+VIC+Australia/?hl=en'
        response = item.scrape_link(url)

        for name, url in response.items():
            print(f'\nName - {name}\nUrl - {url}')

        item.close()
        print("\nAll tests completed.")

    except Exception as e:
        print(f"Error: {e}")
