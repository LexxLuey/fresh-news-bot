from datetime import datetime, timedelta
import os
import re
import openpyxl
import requests
from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Robocloud.Secrets import Secrets
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

browser = Selenium(auto_close=False)

workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.append(
    [
        "Title",
        "Date",
        "Description",
        "Picture Filename",
        "Search Phrase Count",
        "Contains Money",
    ]
)


@task
def extract_data_from_news_site():
    open_news_site()
    enter_search_phrase()
    filter_search_result()
    save_excel()
    clean_up()


def open_news_site():
    browser.open_available_browser("https://www.latimes.com/")


def enter_search_phrase():
    browser.click_element("css:button[data-element='search-button']")
    browser.wait_until_element_is_visible("css:input[data-element='search-form-input']")
    search_phrase = "business"
    browser.input_text(
        "css:input[data-element='search-form-input']", search_phrase + Keys.ENTER
    )

    browser.wait_until_element_is_visible("css:div.select", timeout=30)
    dropdown_element = browser.find_element("css:select.select-input")
    select = Select(dropdown_element)
    select.select_by_visible_text("Newest")
    browser.wait_until_element_is_visible("css:.checkbox-input-label", timeout=10)

    checkbox_labels = browser.find_elements("css:.checkbox-input-label")

    for label in checkbox_labels:
        span_element = label.find_element(By.CSS_SELECTOR, "span")
        span_text = span_element.text.lower()

        if search_phrase in span_text:
            checkbox_input = label.find_element(
                By.CSS_SELECTOR, "input[type='checkbox']"
            )
            checkbox_input.click()
            break


def filter_search_result(months=1):
    current_date = datetime.now()

    start_date = current_date.replace(month=current_date.month - months + 1, day=1)
    if start_date.month < 1:
        start_date = start_date.replace(
            year=start_date.year - 1, month=start_date.month + 12
        )

    last_day_of_month = current_date.replace(
        month=current_date.month % 12 + 1, day=1
    ) - timedelta(days=1)

    if last_day_of_month.month < 1:
        last_day_of_month = last_day_of_month.replace(
            year=last_day_of_month.year - 1, month=last_day_of_month.month + 12
        )

    while True:
        articles = browser.find_elements("css:.search-results-module-results-menu li")

        for article in articles:
            # date_element = article.find_element(By.CSS_SELECTOR, ".promo-timestamp")
            # date_str = date_element.text

            # try:
            #     article_date = datetime.strptime(date_str, "%B %d, %Y")
            # except:
            #     article_date = datetime.strptime(date_str, "%b. %d, %Y")
            date_element = article.find_element(By.CSS_SELECTOR, ".promo-timestamp")
            timestamp = (
                int(date_element.get_attribute("data-timestamp")) / 1000
            )  # Convert to seconds

            # Convert timestamp to datetime object
            article_date = datetime.fromtimestamp(timestamp)
            if article_date < start_date:
                return  # Stop when an article is out of range

            process_article(article)

        # Click "Next" button to go to next page
        try:
            browser.click_element("css:.search-results-module-next-page a")
            browser.wait_until_page_contains_element(
                "css:.search-results-module-results-menu", timeout=30
            )
        except Exception:
            break  # Stop if there's no "Next" button or if unable to click

    browser.wait_until_page_contains_element(
        "css:.search-results-module-results-menu", timeout=30
    )


def process_article(article):
    title: str = article.find_element(By.CSS_SELECTOR, ".promo-title a").text
    date = article.find_element(By.CSS_SELECTOR, ".promo-timestamp").text
    try:
        description = article.find_element(By.CSS_SELECTOR, ".promo-description").text
    except:
        description = "N/A"
    picture_url = article.find_element(
        By.CSS_SELECTOR, ".promo-media img"
    ).get_attribute("src")

    if not description:
        description = "N/A"

    search_phrases = ["business"]  # Add your search phrases here
    title_count = sum(title.lower().count(phrase) for phrase in search_phrases)
    description_count = sum(
        description.lower().count(phrase) for phrase in search_phrases
    )

    money_pattern = r"\$[\d,]+(\.\d{1,2})?|\d+ dollars|\d+ USD"
    contains_money = bool(re.search(money_pattern, title + " " + description))

    words = title.split()
    words = " ".join(words[:5])
    picture_name = words.lower().replace(" ", "_")

    picture_filename = download_news_picture(picture_url, picture_name)

    store_values_in_excel(
        title,
        date,
        description,
        picture_filename,
        title_count + description_count,
        contains_money,
    )


def get_values_in_news_item():
    pass


def store_values_in_excel(
    title, date, description, picture_filename, count, contains_money
):

    worksheet.append(
        [title, date, description, picture_filename, count, contains_money]
    )


def download_news_picture(url, picture_name):
    if not os.path.exists("pictures"):
        os.makedirs("pictures")

    response = requests.get(url)
    
    _, file_extension = os.path.splitext(url)
    
    if file_extension.lower() not in ['.jpg', '.jpeg', '.png']:
        file_extension = ".jpg"
    
    picture_filename = os.path.join("pictures", f"{picture_name}{file_extension}")

    with open(picture_filename, "wb") as file:
        file.write(response.content)

    return picture_filename


def clean_up():
    pass


def save_excel():
    filepath = os.path.join("output", "news_articles.xlsx")
    workbook.save(filepath)
