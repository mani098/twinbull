from datetime import date, timedelta as td

from django.core.management import BaseCommand

from stocks.models import StockHistory


class Command(BaseCommand):
    def run_this(self):

        d1 = date(2017, 02, 24)
        d2 = date(2017, 02, 28)

        delta = d2 - d1

        for i in range(delta.days + 1):
            trade_date = d1 + td(days=i)
            StockHistory.objects.update_stocks(by_trade_date=trade_date)
            print trade_date

    def handle(self, *args, **options):
        StockHistory.objects.update_stocks()
        # self.run_this()
