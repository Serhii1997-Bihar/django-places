from .selenium_launcher import SeleniumDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import time, sys, os, re, requests


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

            time.sleep(2)

            reviews_container = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class, 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde')]",
                    )
                )
            )

            time.sleep(1)

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
                        info = review.find_element(By.CLASS_NAME, "RfnDt ").text.strip()
                        review_text = review.find_elements(
                            By.XPATH, ".//span[@class='wiI7pd']")
                        star_span = review.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
                        date_span = review.find_element(By.CLASS_NAME, "DU9Pgb").find_element(By.CLASS_NAME,
                                                                                              "rsqaWe").text.strip()
                        try:
                            likes_span = review.find_element(By.XPATH, ".//span[contains(@class, 'pkWtMe')]")
                            likes = likes_span.text.strip()
                        except NoSuchElementException:
                            likes = "0"
                        image_buttons = review.find_elements(By.CSS_SELECTOR, "button.Tya61d")
                        images = []
                        for idx, button in enumerate(image_buttons):
                            style = button.get_attribute("style")
                            match = re.search(r'url\("(.+?)"\)', style)
                            if match:
                                img_url = match.group(1)
                                images.append(img_url)

                        review_text = (review_text[0].text.strip() if review_text else None)
                        reviews_list.append(
                            {"Author": author_name, "Review": review_text, "Rating": star_span, "Date": date_span,
                             "Info": info, 'Likes': likes, "Images": images})
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

        try:
            print(f'Reviews {len(reviews_list)} done collected')
        except:
            print("None reviews collected")
        return reviews_list

    def save_images(self, review_dict):
        images_dir = "reviews_images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        images = review_dict.get("Images", [])
        author_name = review_dict.get("Author", "Unknown_Author").replace(" ", "_")

        for idx, img_url in enumerate(images):
            try:
                response = requests.get(img_url, stream=True)
                response.raise_for_status()

                img_filename = os.path.join(images_dir, f"{author_name}_photo_{idx + 1}.jpg")
                img_data = requests.get(img_url, stream=True).content
                with open(img_filename, "wb") as img_file:
                    img_file.write(img_data)

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image!")

    def search_word(self, review_dict, word):
        author_name = review_dict.get("Author", "Unknown Author")
        review_text = review_dict.get("Review", "No text")

        if word.lower() in review_text.lower():
            print("True\n")
        else:
            print("False\n")

    def close(self):
        """Close the Selenium driver."""
        self.driver.quit()

if __name__ == "__main__":
    print("Starting tests for ReviewCollector...\n")

    try:
        driver = SeleniumDriver()
        scraper = ReviewCollector(driver.get_driver())

        url = "https://www.google.com.ua/maps/place/Townhouse/data=!4m7!3m6!1s0x883b2d2564a4a7e5:0x51e005cdf15f1d6a!8m2!3d42.3301258!4d-83.0453143!16s%2Fg%2F11b8t7f546!19sChIJ5aekZCUtO4gRah1f8c0F4FE?authuser=0&hl=en&rclk=1"
        driver.load_url(url)
        print(f'Url - {url}')

        reviews_list = scraper.collect_reviews()
        print(f"Number of reviews collected: {len(reviews_list)}")


        for review in reviews_list:
            print(review)
            scraper.search_word(review_dict=review, word='nice')
            scraper.save_images(review_dict=review)


        scraper.close()
        print("\nAll tests completed.")

    except Exception as e:
        print(e)