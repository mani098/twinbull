import collections

import pandas as pd
from utils.stockstats import StockDataFrame
from datetime import date, timedelta
import datetime

from stocks.models import StockHistory, Stock


class ProcessStragey1(object):
    """trend prediction with macd and cci graph"""

    def __init__(self, symbol):
        self.stock = Stock.objects.get(symbol=symbol)

    def get_macd_data(self):
        # trade_date__range=['2016-01-01', datetime.date.today()]
        queryset = StockHistory.objects.filter(stock_id=self.stock.id,
                                               ).extra(
            select={'date': 'trade_date'}).values(
            'date', 'open', 'high', 'low', 'close')
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
                import ipdb;
                ipdb.set_trace()
                continue

            bought_at = buy_price
            previous_histogram = macd['histogram']
            for trade_date in trade_dates:
                try:

                    current_open = StockHistory.objects.filter(stock_id=self.stock.id,
                                                               trade_date__gt=trade_date).first().open
                except AttributeError as err:
                    print err, 86
                    import ipdb; ipdb.set_trace()
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
