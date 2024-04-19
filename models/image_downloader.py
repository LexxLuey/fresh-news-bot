import logging
import os
import requests


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
class ImageDownloader:

    @classmethod
    def download_news_picture(self, url, picture_name):
        logger.info("downloading image...")
        try:            
            if not os.path.exists("output/pictures"):
                os.makedirs("output/pictures")

            response = requests.get(url)

            _, file_extension = os.path.splitext(url)

            if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
                file_extension = ".jpg"

            picture_filename = os.path.join(
                "output/pictures", f"{picture_name}{file_extension}"
            )

            with open(picture_filename, "wb") as file:
                file.write(response.content)

            logger.info("downloading complete...")
            return picture_filename

        except Exception:
            logger.exception("Could not download image...")

