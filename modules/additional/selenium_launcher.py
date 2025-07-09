from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumDriver:
    def __init__(self, headless=True):
        """Initialize the Selenium WebDriver with options."""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    def load_url(self, url):
        """Load a URL in the Selenium WebDriver."""
        try:
            self.driver.get(url)
            print('Url loaded')
            sleep(1)
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            return False
        return True

    def get_driver(self):
        """Return the Selenium WebDriver instance."""
        return self.driver

    def quit(self):
        """Close the Selenium WebDriver instance."""
        self.driver.quit()