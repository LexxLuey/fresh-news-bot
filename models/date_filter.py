from datetime import datetime, timedelta


class DateFilter:

    @classmethod
    def date_calcs(self, months):
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

        return start_date
