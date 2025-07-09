from selenium_launcher import SeleniumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time, sys


class ReviewCollector:
    def __init__(self, driver:SeleniumDriver):
        """Initialize ReviewCollector with a Selenium driver, max review count, and max time limit."""
        self.driver = driver
        
    def collect_reviews(self):
        print('Start scraping reviews')
        """Collect reviews up to a specified maximum count or timeout."""
        reviews_list = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label, 'Reviews')]")
                )
            ).click()
            
            reviews_container = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class, 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde')]",
                    )
                )
            )

            unique_reviews = set()
            max_reviews = 10
            print(f"Maximum reviews to collect: {max_reviews}")

            previous_count = set()  # Tracks the previous count of unique reviews
            no_new_reviews_limit = 3  # Number of iterations without new reviews before stopping
            no_new_reviews_count = 0

            while len(unique_reviews) < max_reviews:
                try:
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", reviews_container)
                except StaleElementReferenceException:
                    print("Failed to scroll the reviews container.")
                    break
                
                reviews_elements = self.driver.find_elements(By.XPATH, "//div[@data-review-id]")

                for review in reviews_elements:
                    review_id = review.get_attribute("data-review-id")
                    if review_id not in unique_reviews:
                        unique_reviews.add(review_id)
                        author_name = review.get_attribute("aria-label").strip()
                        review_text = review.find_elements(
                            By.XPATH, ".//span[@class='wiI7pd']"
                        )
                        review_text = (
                            review_text[0].text.strip() if review_text else None
                        )
                        reviews_list.append(
                            {"Author": author_name, "Review": review_text}
                        )
                        if len(unique_reviews) >= max_reviews:
                            break
                
                # Check if the number of reviews is still growing
                if len(unique_reviews) == len(previous_count):
                    no_new_reviews_count += 1
                    print(f"No new reviews added. Attempt {no_new_reviews_count}/{no_new_reviews_limit}")
                    if no_new_reviews_count >= no_new_reviews_limit:
                        print("Stopping collection: No new reviews found after multiple attempts.")
                        break
                else:
                    no_new_reviews_count = 0  # Reset the counter if new reviews are found

                previous_count = unique_reviews

        except TimeoutException:
            print("Failed to download or collect reviews.")
        
        if not reviews_list:
            reviews_list = None
        
        print('Reviews done', f'{len(reviews_list)} collected')
        return reviews_list

    def close(self):
        """Close the Selenium driver."""
        self.driver.quit()


# Отдельный тест класса
if __name__ == "__main__":
    print("Starting tests for ReviewCollector...\n")

    try:
        driver = SeleniumDriver()
        scraper = ReviewCollector(driver.get_driver())

        url = 'https://www.google.com.ua/maps/place/Solpoint+Accounts+Pty+Ltd/@-37.8112811,144.9640491,17z/data=!3m1!5s0x6ad642ca60aab5f5:0xc7fb23d9f355a38f!4m8!3m7!1s0x6ad642ca5885aba9:0x4c4f0893bf0a06c8!8m2!3d-37.8112811!4d144.9640491!9m1!1b1!16s%2Fg%2F1thtpr2k?authuser=0&hl=en&entry=ttu&g_ep=EgoyMDI0MTExOS4yIKXMDSoASAFQAw%3D%3D'
        driver.load_url(url)
        print(f'Url - {url}')

        reviews_list = scraper.collect_reviews()

        print(f"Number of reviews collected: {len(reviews_list)}")
        for review in reviews_list:
            print(review)

        scraper.close()
        print("\nAll tests completed.")

    except Exception as e:
        print(e)