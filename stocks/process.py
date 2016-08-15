from models import StockHistory, StockProcessed
from utils.nse_bhav import Nse
from datetime import date, timedelta
from django.db.models import F, Q


class FilteredStock(object):

    @classmethod
    def get_data(cls, trade_date=date.today()):
        stocks_qs = StockHistory.objects\
                            .annotate(today_change=F('close') - F('open'),
                                      prev_change=F('close') - F('prev_close')) \
                            .filter(total_traded_quantity__gte=10000)\
                            .filter(close__range=[15, 1000]) \
                            .filter(trade_date=trade_date) \
                            .filter(Q(today_change__range=[11, 25]) | Q(today_change__range=[-11, -25])) \
                            .order_by('stock_symbol').select_related('stock_symbol')

        filtered_stocks = []
        for stock in stocks_qs:
            delivered_quantity = Nse.deliverables(stock.stock_symbol.symbol)
            if delivered_quantity > 65 and stock.prev_change >= stock.prev_close/100:
                filtered_stocks.append(
                    StockProcessed(stock_history_id=stock.id, deliverables=delivered_quantity)
                )
        return StockProcessed.objects.bulk_create(filtered_stocks)
