from django.core.management import BaseCommand
from stocks.models import StockHistory


class Command(BaseCommand):

    def handle(self, *args, **options):
        StockHistory.objects.update_stocks()