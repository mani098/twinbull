from django.core.management import BaseCommand

from stocks.models import StockOrder
from utils.util import NseHelper
from utils.util import send_via_telegram
from time import sleep


class Command(BaseCommand):
    def _get_stock_quotes(self):
        stock_symbols = StockOrder.objects.filter(status=StockOrder.BOUGHT).values_list('stock_history__stock__symbol',
                                                                                        flat=True)
        stock_quotes = NseHelper().stock_quotes(list(stock_symbols))
        return stock_quotes

    def _stock_target(self, trade_close, cmp):
        """Check for 3% target or -2% stop-loss"""

        # cmp -> current market price
        change = (100 / trade_close) * (cmp - trade_close)

        if change >= 3 or change <= -2:
            sell = True
        else:
            sell = False
        return '%.2f' % change, sell

    def _trigger_monitor(self):
        stock_quotes = self._get_stock_quotes()
        for stock in stock_quotes:
            stock_symbol = stock['symbol'].replace('&amp;', '&')
            stock_order = StockOrder.objects.select_related('stock_history__stock', 'stock_history'). \
                filter(stock_history__stock__symbol=stock_symbol).last()

            avg_price = float(stock['averagePrice'].replace(',', ''))
            bought_price = stock_order.stock_history.close
            price_change, is_sell = self._stock_target(bought_price, avg_price)

            if is_sell:
                stock_order.status = StockOrder.SOLD
                stock_order.save(update_fields=['status'])
                text = 'Sell {} @ Rs. {} \n Bought @ {} Rs. {} \n Profit: {}%'.format(stock_symbol, avg_price,
                                                                                      stock_order.stock_history.trade_date,
                                                                                      bought_price,
                                                                                      price_change)
                send_via_telegram(text)

    def handle(self, *args, **options):
        while True:
            self._trigger_monitor()
            sleep(60*5)
