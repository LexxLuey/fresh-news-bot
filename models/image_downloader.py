import os

import requests


class ImageDownloader:

    @classmethod
    def download_news_picture(self, url, picture_name):
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

        return picture_filename
