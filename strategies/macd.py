import collections

import pandas as pd
from utils.stockstats import StockDataFrame
from datetime import date, timedelta

from stocks.models import StockHistory, Stock
import logging

logger = logging.getLogger(__name__)


class MacdStrategy(object):
    def __init__(self):
        self.today = date.today()

    def get_signals(self, signal_type):
        """Get signals by `buy` or `sell` """
        assert signal_type, "signal_type is required"
        signal_method = '{}_signals'.format(signal_type)
        getattr(self, signal_method)()

    def get_macd(self, stock_id):
        """Get macd data for an year and return only last 2 traded dates"""
        queryset = StockHistory.objects.filter(stock_id=stock_id,
                                               trade_date__range=['2016-01-01', self.today]) \
            .extra(select={'date': 'trade_date'}).values('date', 'close')
        stockdataframe = StockDataFrame.retype(pd.DataFrame.from_records(queryset))
        histogram = stockdataframe['macdh'].to_dict()
        macd_results = {
            trade_date: {'histogram': histogram[trade_date]} for trade_date in sorted(histogram.keys())[-2:]}
        return macd_results

    def buy_signals(self):
        stocks = StockHistory.objects.select_related('stock').filter(total_traded_qty__gt=100000, close__gt=50,
                                                                     trade_date=self.today)

        stocks_count = stocks.count()

        if stocks_count == 0:
            logger.info("No data exists")
            return
        logger.info('Total eligible stocks: %d' % stocks_count)
        total_buy_signals = 0

        for stock in stocks:
            macd_results = self.get_macd(stock_id=stock.stock.id)
            if not bool(macd_results) or self.today not in macd_results:
                continue
            cur_histogram = macd_results.pop(self.today)['histogram']
            prev_histogram = macd_results.pop(macd_results.keys()[0])['histogram']
            stock_history_obj = stocks.get(trade_date=self.today)
            if 0 > cur_histogram > prev_histogram and not stock_history_obj.watch_list:
                stock_history_obj.watch_list = True
                stock_history_obj.is_filtered = True
                stock_history_obj.save(update_fields=['watch_list', 'is_filtered'])
                total_buy_signals += 1
        logger.info("Buy signals updated in watch list: %d/%d" % (total_buy_signals, stocks_count))

    def sell_signals(self):
        stocks = StockHistory.objects.select_related('stock').filter(watch_list=True, is_filtered=True)
        stocks_count = stocks.count()
        if stocks_count == 0:
            logger.info("No data exists")
            return

        total_sell_signals = 0
        for stock in stocks:
            macd_results = self.get_macd(stock_id=stock.stock.id)

            if not bool(macd_results) or self.today not in macd_results:
                continue
            cur_histogram = macd_results.pop(self.today)['histogram']
            prev_histogram = macd_results.pop(macd_results.keys()[0])['histogram']
            stock_history_obj = stocks.get(trade_date=self.today)

            if cur_histogram < prev_histogram:
                # stock_history_obj.is_filtered = False
                # stock_history_obj.save(update_fields=['is_filtered'])
                # total_sell_signals += 1
                print stock_history_obj.stock.symbol
        logger.info("Sell signals updated in watch list: %d/%d" % (total_sell_signals, stocks_count))


class ProcessStrategy1(object):
    """Trend prediction with macd and cci graph"""

    def __init__(self, symbol):
        self.stock = Stock.objects.get(symbol=symbol)

    def get_macd_data(self):
        # trade_date__range=['2016-01-01', datetime.date.today()]
        queryset = StockHistory.objects.filter(stock_id=self.stock.id,
                                               ).extra(
            select={'date': 'trade_date'}).values(
            'date', 'close')
        stockdataframe = StockDataFrame.retype(pd.DataFrame.from_records(queryset))

        histogram = stockdataframe['macdh'].to_dict()
        signal_line = stockdataframe['macds'].to_dict()
        macd_line = stockdataframe['macd'].to_dict()

        macd_data = {}
        for date in histogram.keys():
            macd_data[date] = {'histogram': histogram[date], 'macd_line': macd_line[date],
                               'signal_line': signal_line[date]
                               }
            # macd_data[date] = {'histogram': histogram[date]}
        macd_data = collections.OrderedDict(sorted(macd_data.items()))

        # for date, macd_result in macd_data.iteritems():
        #     print date, StockHistory.objects.get(trade_date=date, stock_id=self.stock.id).close, macd_result[
        #         'macd_line'], macd_result['signal_line'], macd_result['histogram']
        return macd_data

    def backtest(self):
        data = self.get_macd_data()
        buy_signals = collections.OrderedDict()
        prev_point = 0
        for index, signal in enumerate(data.iterkeys()):
            histogram = data[signal]['histogram']
            # print '%s\t%f' % (signal, histogram)
            if index == 26:
                prev_point = histogram
            elif index > 26:
                # if histogram > 0 and prev_point < 0:
                if histogram > prev_point and histogram < 0:
                    buy_signals[signal] = data[signal]
                prev_point = histogram

        print 'Days\tBuy date\tB.price\tSell_date\tSold_at\tProf.%\tProfit'
        n_profit = 0
        n_neutral = 0
        n_negative = 0

        total_buy_signals = len(buy_signals)
        for buy_date, macd in buy_signals.iteritems():
            trade_dates = filter(lambda x: x > buy_date, data)
            profit = 0
            try:
                buy_price = StockHistory.objects.filter(stock_id=self.stock.id,
                                                        trade_date__gt=buy_date).first().open
            except AttributeError as err:
                print err, 73
                continue

            bought_at = buy_price
            previous_histogram = macd['histogram']
            for trade_date in trade_dates:
                try:

                    current_open = StockHistory.objects.filter(stock_id=self.stock.id,
                                                               trade_date__gt=trade_date).first().open
                except AttributeError as err:
                    print err, 86
                    continue
                profit += current_open - buy_price
                buy_price = current_open

                if data[trade_date]['histogram'] > previous_histogram:
                    previous_histogram = data[trade_date]['histogram']
                else:
                    if profit > 0:
                        n_profit += 1
                    elif profit < 0:
                        n_negative += 1
                    elif profit == 0:
                        n_neutral += 1
                    print '%s\t%s\t%.1f\t%s\t%.1f\t%.2f%%\t%.2f' % (
                        (trade_date - buy_date).days, buy_date + timedelta(days=1), bought_at,
                        trade_date + timedelta(days=1), current_open,
                        (100 / bought_at) * profit, profit)
                    break

        print "Total buy signals: %s" % total_buy_signals
        print "Accuracy: Positive: %s\tNegative: %s\tNeutral: %s" % (n_profit, n_negative, n_neutral)
