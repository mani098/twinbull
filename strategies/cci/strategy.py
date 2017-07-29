import logging
from datetime import date, timedelta
from django.db.models import F

from stocks.models import StockHistory, StockOrder
from utils.util import send_via_telegram, get_quarter_month
from .cci import CommodityChannelIndex

logger = logging.getLogger(__name__)


# Make sure when before you buy, check cci manually(May be automated) whether it is oversold

class CciStrategy(object):
    def __init__(self):
        # self.today = date.today()
        self.today = date(2017, 6, 12)

    def is_valid_buy(self, stock_obj, cci_data):
        curr_cci = cci_data[1]
        prev_histogram = cci_data[0]
        is_valid_cci = curr_cci >= -100 > prev_histogram

        return is_valid_cci

    def get_signals(self, signal_type):
        """Get signals by `buy` or `sell` """
        assert signal_type, "signal_type is required"
        signal_method = '{}_signals'.format(signal_type)
        logger.info("Running {} for trade date: {}".format(signal_type, self.today))
        getattr(self, signal_method)()

    def buy_signals(self):
        existing_orders = StockOrder.objects.filter(status=StockOrder.BOUGHT).values_list('stock_history_id', flat=True)
        stocks = StockHistory.objects.select_related('stock').filter(trade_date=self.today, total_traded_qty__gt=300000,
                                                                     close__gte=21). \
            annotate(day_change_percent=(100 / F('open') * (F('close') - F('open')))).filter(day_change_percent__lt=5,
                                                                                             day_change_percent__gt=0). \
            exclude(stock__symbol='LIQUIDBEES', id__in=existing_orders)
        stocks_count = stocks.count()

        if stocks_count == 0:
            logger.info("No data exists")
            return
        logger.info('Total eligible stocks: %d' % stocks_count)
        tot_buy_signals = 0
        text = 'BUY @ {}\n\n'.format(self.today + timedelta(days=1))

        for stock in stocks:
            cci_result = CommodityChannelIndex(stock_id=stock.stock_id, last_trade_date=self.today).get_data()

            if not bool(cci_result) or self.today not in cci_result:
                # If cci data is Null continue with next available stock
                logging.info("`{}` no CCI data available".format(stock.stock.symbol))
                continue

            cci_result = list(cci_result.values())

            if len(cci_result) < 2:
                # To prevent the IPO stocks started traded on self.today
                logging.info("`{}` might be a IPO stock".format(stock.stock.symbol))
                continue

            if self.is_valid_buy(stock_obj=stock, cci_data=cci_result):
                stock_history_obj = stocks.get(stock_id=stock.stock_id, trade_date=self.today)

                # Create a record in StockOrder table, default status would be BOUGHT
                StockOrder.objects.create(stock_history_id=stock_history_obj.id)

                # Generate the text for the filtered buy signal stock to send via telegram
                tot_buy_signals += 1
                text += '{0}.\t{1}\tRs.{2}\n'.format(tot_buy_signals, stock.stock.symbol, stock.close)

        if tot_buy_signals > 0:
            send_via_telegram(text)
        logger.info("Buy signals updated in watch list: %d/%d" % (tot_buy_signals, stocks_count))
