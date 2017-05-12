from datetime import date, timedelta as td

from django.core.management import BaseCommand

from stocks.models import StockHistory


class Command(BaseCommand):
    def run_this(self):
        d1 = StockHistory.objects.last().trade_date + td(days=1)
        d2 = date.today()

        delta = d2 - d1

        for i in range(delta.days + 1):
            trade_date = d1 + td(days=i)
            StockHistory.objects.update_stocks(by_trade_date=trade_date)

    def handle(self, *args, **options):
        # StockHistory.objects.update_stocks()
        self.run_this()
