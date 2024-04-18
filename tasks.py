import logging
from robocorp.tasks import task
from robocorp import workitems

from models.newscraper import NewsSiteScraper


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@task
def extract_data_from_news_site():
    logger.info("Retrieve current work items...")
    item = workitems.inputs.current

    logger.info("Extract parameters from payload...")
    search_phrase = item.payload.get("search_phrase", "")
    category = item.payload.get("category", "")
    months = item.payload.get("months", 1)

    logger.info("Initializing news scrapper...")
    news_scraper = NewsSiteScraper

    news_scraper.open_news_site()
    news_scraper.enter_search_phrase(search_phrase=search_phrase, category=category)
    news_scraper.filter_search_result(months=months, search_phrase=search_phrase)
    news_scraper.save_excel()
