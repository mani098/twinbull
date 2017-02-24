from django.core.management import BaseCommand
from strategies.macd import ProcessStragey1


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('symbol', nargs='+', type=str)

    def handle(self, *args, **options):
        return ProcessStragey1(options['symbol'][0]).backtest()
