import logging
from datetime import date, timedelta

from stocks.models import StockHistory
from utils.util import send_via_telegram, get_quarter_month
from .macd import Macd
from django.db.models import F

logger = logging.getLogger(__name__)


class MacdStrategy(object):
    """Don't run this strategy during the first 5 trading days of quarter,
     if we try to run at this time then eventually the results would be wrong"""

    def __init__(self):
        # self.today = date.today()
        self.today = date(2017, 5, 4)

    def get_signals(self, signal_type):
        """Get signals by `buy` or `sell` """
        assert signal_type, "signal_type is required"
        signal_method = '{}_signals'.format(signal_type)
        logger.info("Running {} for trade date: {}".format(signal_type, self.today))
        getattr(self, signal_method)()

    def is_valid_buy(self, stock_obj, histograms):
        """Validate the stock to identify it's trend"""
        curr_histogram = histograms[1]
        prev_histogram = histograms[0]
        is_valid_histogram = curr_histogram >= 0 > prev_histogram

        quarter_month = get_quarter_month(stock_obj.trade_date)
        quarter_prices = StockHistory.objects. \
                             filter(stock_id=stock_obj.stock_id, trade_date__month=quarter_month,
                                    trade_date__year=stock_obj.trade_date.year). \
                             order_by('trade_date').values_list('close', flat=True)[:5]

        if not quarter_prices:
            # Check the quarterly growth
            return False

        is_valid_quarter = True
        for price in list(quarter_prices):
            if stock_obj.close < price:
                # If current price is lesser than the quarter initial price then it's not a valid buy
                is_valid_quarter = False
                break

        # prev_histogram should be < 0 and curr_histogram should be >=0 to identify the up-trend
        return is_valid_quarter and is_valid_histogram

    def buy_signals(self):
        """Filter stocks which are eligible for buy and send the signal via telegram"""

        stocks = StockHistory.objects.select_related('stock').filter(trade_date=self.today, total_traded_qty__gt=300000,
                                                                     watch_list=False, close__gte=21). \
            annotate(day_change_percent=(100 / F('open') * (F('close') - F('open')))).filter(day_change_percent__lt=5,
                                                                                             day_change_percent__gt=0). \
            exclude(stock__symbol='LIQUIDBEES')
        stocks_count = stocks.count()

        if stocks_count == 0:
            logger.info("No data exists")
            return

        logger.info('Total eligible stocks: %d' % stocks_count)
        tot_buy_signals = 0
        text = 'BUY @ {}\n\n'.format(self.today + timedelta(days=1))

        for stock in stocks:
            macd_result = Macd(stock_id=stock.stock_id, last_trade_date=self.today).get_histogram()
            if not bool(macd_result) or self.today not in macd_result:
                continue
            histograms = list(map(lambda x: x['histogram'], macd_result.values()))

            if len(histograms) < 2:
                # To prevent the IPO stocks started traded on self.today
                continue

            if self.is_valid_buy(stock_obj=stock, histograms=histograms):
                stock_history_obj = stocks.get(stock_id=stock.stock_id, trade_date=self.today)
                stock_history_obj.watch_list = True
                stock_history_obj.save(update_fields=['watch_list'])

                # Generate the text for the filtered buy signal stock to send via telegram
                tot_buy_signals += 1
                text += '{0}.\t{1}\tRs.{2}\n'.format(tot_buy_signals, stock.stock.symbol, stock.close)

        if tot_buy_signals > 0:
            send_via_telegram(text)

        logger.info("Buy signals updated in watch list: %d/%d" % (tot_buy_signals, stocks_count))

    def sell_signals(self):
        stocks = StockHistory.objects.select_related('stock').filter(watch_list=True, is_filtered=False).order_by(
            'stock__symbol')
        stocks_count = stocks.count()
        if stocks_count == 0:
            logger.info("No data exists")
            return

        total_sell_signals = 0
        text = 'SELL @ {}\n\n'.format(self.today + timedelta(days=1))

        for stock in stocks:
            macd_result = Macd(stock_id=stock.stock_id, last_trade_date=self.today).get_histogram(days=1)
            if not bool(macd_result) or self.today not in macd_result:
                continue

            cur_histogram = macd_result.pop(self.today)['histogram']
            stock_history_obj = StockHistory.objects.get(stock_id=stock.stock_id, trade_date=self.today)

            if cur_histogram <= 0:
                total_sell_signals += 1
                profit = (100 / stock.close) * (stock_history_obj.close - stock.close)
                text += '{0}.\t{1}\t{2}\tRs.{3}\t{4:.2f}%\n'.format(total_sell_signals, stock.trade_date,
                                                                    stock.stock.symbol, stock_history_obj.close,
                                                                    profit)
                stock.comments = 'SOLD @ {0}  {1:.2f}%'.format(stock_history_obj.close, profit)
                stock.is_filtered = True
                stock.save(update_fields=['comments', 'is_filtered'])
        if total_sell_signals > 0:
            send_via_telegram(text)
        logger.info("Sell signals updated in watch list: %d/%d" % (total_sell_signals, stocks_count))
