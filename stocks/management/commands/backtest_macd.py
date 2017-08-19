from django.core.management import BaseCommand
from strategies.macd import MacdStrategy
from datetime import date


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('signal', nargs='+', type=str)

    def handle(self, *args, **options):
        signal = options['signal'][0]
        MacdStrategy().get_signals(signal_type=signal)

        # self._back_test_macd(signal)

    def _back_test_macd(self, signal):
        for i in range(1, 30):
            trigger_date = date(2017, 6, i)
            MacdStrategy(trigger_date=trigger_date).get_signals(signal_type=signal)
