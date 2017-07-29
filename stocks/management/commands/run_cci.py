from django.core.management import BaseCommand
from strategies.cci.strategy import CciStrategy


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('signal', nargs='+', type=str)

    def handle(self, *args, **options):
        signal = options['signal'][0]
        return CciStrategy().get_signals(signal_type=signal)
