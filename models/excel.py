import os
import openpyxl


class ExcelWriter:

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

    @classmethod
    def store_values_in_excel(
        self, title, date, description, picture_filename, count, contains_money
    ):

        self.worksheet.append(
            [title, date, description, picture_filename, count, contains_money]
        )

    @classmethod
    def save_excel(self):
        filepath = os.path.join("output", "news_articles.xlsx")
        self.workbook.save(filepath)
