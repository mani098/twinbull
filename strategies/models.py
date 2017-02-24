from django.db import models
from stocks.models import StockHistory, Stock


class Macd(models.Model):
    stock_history = models.ForeignKey(StockHistory, db_index=True)
    XII_day_ema = models.FloatField(blank=True, null=True)
    XXVI_day_ema = models.FloatField(blank=True, null=True)
    macd_line = models.FloatField(blank=True, null=True)
    signal_line = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        print '%s - %s - %s' % (self.stock_history.trade_date, self.macd_line, self.signal_line)
