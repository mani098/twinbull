from datetime import date

import pandas as pd
from collections import OrderedDict

from stocks.models import StockHistory
from utils.stockstats import StockDataFrame


class CommodityChannelIndex(object):
    def __init__(self, stock_id, last_trade_date=date.today()):
        self.stock_id = stock_id
        self.last_trade_date = last_trade_date
        self.period = 5

    def get_data(self, days=5):
        queryset = StockHistory.objects.filter(stock_id=self.stock_id,
                                               trade_date__range=['2017-01-01', self.last_trade_date]). \
            extra(select={'date': 'trade_date'}).values('date', 'close', 'high', 'low')

        stock_data_frame = StockDataFrame.retype(pd.DataFrame.from_records(queryset))
        cci_data = stock_data_frame['cci_{}'.format(self.period)]

        cci_results = OrderedDict(
            (trade_date, cci_data[trade_date]) for trade_date in sorted(cci_data.keys()[-days:])
        )
        return cci_results
