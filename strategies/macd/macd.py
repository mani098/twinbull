import pandas as pd
from collections import OrderedDict

from stocks.models import StockHistory
from utils.stockstats import StockDataFrame


class Macd(object):
    def __init__(self, stock_id, last_trade_date):
        self.stock_id = stock_id
        self.last_trade_date = last_trade_date

    def get_histogram(self, days=2):
        """Get macd data for an year and return only last 2 traded date"""
        queryset = StockHistory.objects.filter(stock_id=self.stock_id,
                                               trade_date__range=['2016-05-01', self.last_trade_date]) \
            .extra(select={'date': 'trade_date'}).values('date', 'close')
        stock_data_frame = StockDataFrame.retype(pd.DataFrame.from_records(queryset))
        histogram = stock_data_frame['macdh'].to_dict()

        macd_results = OrderedDict(
            (trade_date, {'histogram': histogram[trade_date]}) for trade_date in sorted(histogram.keys())[-days:])
        return macd_results
