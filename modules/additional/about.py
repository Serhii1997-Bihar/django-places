from time import sleep

from .selenium_launcher import SeleniumDriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


class AboutCollector:
    def __init__(self, driver:SeleniumDriver):
        """Initialize AboutCollector with a Selenium driver."""
        self.driver = driver
        
    def collect_about(self):
        
        print('Start scraping about')
        
        """Collect 'About' information by extracting categories and their elements using precise XPath."""
        try:
            # Open the ‘About’ tab
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@role='tab' and contains(@aria-label, 'About')]",)
                )).click()
            sleep(1.5)

            # Find the main container with the ‘About’ information
            about_section = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH,"//div[contains(@class, 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde')]",)
                ))

            # Find all category headings (<h2> elements)
            categories = about_section.find_elements(By.XPATH, ".//h2")
            about_info = []

            for category in categories:
                category_name = category.text.strip()
                if not category_name:
                    continue

                # Looking for items belonging to the current category
                ul_element = category.find_element(
                    By.XPATH, "./following-sibling::ul[1]"
                )
                items = ul_element.find_elements(By.XPATH, ".//li//span[@aria-label]")

                # Save items of the current category
                category_items = [
                    item.text.strip() for item in items if item.text.strip()
                ]

                # If there are items for a category, add them to the list
                if category_items:
                    about_info.append(f'{category_name}:{category_items}')
            
            if not about_info:
                about_info = None
                
            print("Succesfull to load 'About' section.")
            return about_info

        except (TimeoutException, NoSuchElementException):
            print("Failed to load 'About' section.")
            return []
    
    def close(self):
        """Close the Selenium driver."""
        self.driver.quit()


# Отдельный тест класса
if __name__ == "__main__":
    print("Starting tests for AboutCollector...\n")

    try:
        driver = SeleniumDriver()
        scraper = AboutCollector(driver.get_driver())

        url = 'https://www.google.com.ua/maps/place/WITH+ACCOUNTING/data=!4m7!3m6!1s0x6ad65d4c478de8e7:0x1aa3800673684e1b!8m2!3d-37.8168643!4d144.9570784!16s%2Fg%2F11cm3hy068!19sChIJ5-iNR0xd1moRG05ocwaAoxo?authuser=0&hl=en&rclk=1'
        driver.load_url(url)
        print(f'Url - {url}')

        about = scraper.collect_about()

        print(about)

        scraper.close()
        print("\nAll tests completed.")

    except Exception as e:
        print(e)