from django.core.management import BaseCommand
from strategies.macd import MacdStrategy


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('signal', nargs='+', type=str)

    def handle(self, *args, **options):
        signal = options['signal'][0]
        return MacdStrategy().get_signals(signal_type=signal)
