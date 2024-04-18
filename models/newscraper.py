from datetime import datetime
import re
import logging
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from models.date_filter import DateFilter
from models.excel import ExcelWriter
from models.image_downloader import ImageDownloader


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class NewsSiteScraper:

    browser = Selenium()
    url = "https://www.latimes.com/"
    excel = ExcelWriter

    def __init__(self):
        logger.info("Initializing NewsSiteScraper...")
        # ...

    @classmethod
    def open_news_site(self):
        self.browser.open_available_browser(self.url)
        logger.info("Opening site...")

    @classmethod
    def enter_search_phrase(self, search_phrase: str = "", category: str = ""):
        logger.info(f"Searching for {search_phrase} in {category} section...")

        self.browser.click_element("css:button[data-element='search-button']")
        self.browser.wait_until_element_is_visible(
            "css:input[data-element='search-form-input']"
        )
        self.browser.input_text(
            "css:input[data-element='search-form-input']", search_phrase + Keys.ENTER
        )

        self.browser.wait_until_element_is_visible("css:div.select", timeout=30)
        dropdown_element = self.browser.find_element("css:select.select-input")
        select = Select(dropdown_element)
        select.select_by_value("1")
        self.browser.wait_until_element_is_visible(
            "css:.checkbox-input-label", timeout=10
        )

        checkbox_labels = self.browser.find_elements("css:.checkbox-input-label")

        for label in checkbox_labels:
            span_element = label.find_element(By.CSS_SELECTOR, "span")
            span_text = span_element.text.lower()

            if category.lower() in span_text:
                checkbox_input = label.find_element(
                    By.CSS_SELECTOR, "input[type='checkbox']"
                )
                checkbox_input.click()
                break

    @classmethod
    def filter_search_result(self, months: int = 1, search_phrase: str = ""):
        logger.info("Processing search results...")
        date_filter = DateFilter
        start_date = date_filter.date_calcs(months)

        while True:
            articles = self.browser.find_elements(
                "css:.search-results-module-results-menu li"
            )

            for article in articles:
                date_element = article.find_element(By.CSS_SELECTOR, ".promo-timestamp")
                timestamp = (
                    int(date_element.get_attribute("data-timestamp")) / 1000
                )  # Convert to seconds

                article_date = datetime.fromtimestamp(timestamp)
                if article_date < start_date:
                    logger.info("Found all articles within given range...")
                    return  # Stop when an article is out of range

                self.process_article(article, search_phrase)

            # Click "Next" button to go to next page
            try:
                self.browser.click_element("css:.search-results-module-next-page a")
                self.browser.wait_until_page_contains_element(
                    "css:.search-results-module-results-menu", timeout=30
                )
            except Exception:
                logger.info("No Next Button, Proceeding...")
                break  # Stop if there's no "Next" button or if unable to click

        self.browser.wait_until_page_contains_element(
            "css:.search-results-module-results-menu", timeout=30
        )

    @classmethod
    def process_article(self, article, search_phrase: str):
        logger.info("Processing an article...")

        title: str = article.find_element(By.CSS_SELECTOR, ".promo-title a").text
        date = article.find_element(By.CSS_SELECTOR, ".promo-timestamp")
        timestamp = int(date.get_attribute("data-timestamp")) / 1000

        article_date = datetime.fromtimestamp(timestamp)
        date = article_date.strftime("%B %d, %Y")
        try:
            description = article.find_element(
                By.CSS_SELECTOR, ".promo-description"
            ).text
        except Exception:
            description = "N/A"
        picture_url = article.find_element(
            By.CSS_SELECTOR, ".promo-media img"
        ).get_attribute("src")

        if not description:
            description = "N/A"

        search_phrases = search_phrase.lower().split()
        title_count = sum(title.lower().count(phrase) for phrase in search_phrases)
        description_count = sum(
            description.lower().count(phrase) for phrase in search_phrases
        )

        money_pattern = r"\$[\d,]+(\.\d{1,2})?|\d+ dollars|\d+ USD"
        contains_money = bool(re.search(money_pattern, title + " " + description))

        words = title.split()
        words = " ".join(words[:5])
        picture_name = words.lower().replace(" ", "_")
        image_downloader = ImageDownloader

        picture_filename = image_downloader.download_news_picture(
            picture_url, picture_name
        )

        self.excel.store_values_in_excel(
            title,
            date,
            description,
            picture_filename,
            title_count + description_count,
            contains_money,
        )

        logger.info("Article processed, data possessed.")

    @classmethod
    def save_excel(self):
        self.excel.save_excel()
        logger.info("Saving...")
