import collections

import pandas as pd
from stockstats import StockDataFrame

from stocks.models import StockHistory, Stock


class ProcessStragey1(object):
    """trend prediction with macd and cci graph"""

    def __init__(self, symbol):
        self.stock = Stock.objects.get(symbol=symbol)

    def get_macd_data(self):
        queryset = StockHistory.objects.filter(stock_id=self.stock.id).extra(select={'date': 'trade_date'}).values(
            'date', 'open', 'high', 'low', 'close')
        stockdataframe = StockDataFrame.retype(pd.DataFrame.from_records(queryset))

        macd_line = stockdataframe['macd'].to_dict()
        signal_line = stockdataframe['macds'].to_dict()
        histogram = stockdataframe['macdh'].to_dict()

        macd_data = {}
        for date in macd_line.keys():
            macd_data[date] = {'macd_line': macd_line[date], 'signal_line': signal_line[date],
                               'histogram': histogram[date]}
        macd_data = collections.OrderedDict(sorted(macd_data.items()))
        return macd_data

    def backtest(self):
        data = self.get_macd_data()
        buy_signals = collections.OrderedDict((i, j) for i, j in data.iteritems() if 0 < j['histogram'] < 1)

        print 'days\tBuy date\tB.price\tSell date\tSold at\tprof.%\tprofit'
        for buy_date, macd in buy_signals.iteritems():
            trade_dates = filter(lambda x: x > buy_date, data)
            profit = 0
            prev_close = StockHistory.objects.get(stock_id=self.stock.id, trade_date=buy_date).close
            bought_at = prev_close
            previous_histogram = macd['histogram']
            for trade_date in trade_dates:
                if data[trade_date]['histogram'] > previous_histogram:
                    current_close = StockHistory.objects.get(stock_id=self.stock.id, trade_date=trade_date).close
                    profit += current_close - prev_close
                    prev_close = current_close
                    previous_histogram = data[trade_date]['histogram']
                else:
                    if profit != 0:
                        print '%s\t%s\t%.1f\t%s\t%.1f\t%.2f%%\t%.2f' % (
                            (trade_date-buy_date).days,buy_date, bought_at, trade_date, prev_close, (100 / bought_at) * profit, profit)
                    break

        print "Total buy signals: %s" % len(buy_signals)
