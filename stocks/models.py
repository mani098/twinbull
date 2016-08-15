from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=100, verbose_name="Symbol")
    isin = models.CharField(max_length=30, verbose_name="ISIN")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Stock created at")

    def __str__(self):
        return self.symbol


class StockHistory(models.Model):
    stock = models.ForeignKey(Stock)
    created_at = models.DateTimeField(auto_now_add=True)
    trade_date = models.DateField(verbose_name="Traded date")
    open = models.FloatField(verbose_name="Open price")
    high = models.FloatField(verbose_name="High price")
    low = models.FloatField(verbose_name="Low price")
    close = models.FloatField(verbose_name="Low price")
    prev_close = models.FloatField(verbose_name="Previous Close value")
    total_traded_qty = models.IntegerField(verbose_name="Total Traded quantity")
    total_traded_value = models.FloatField(verbose_name="Total Traded value")
    total_trades = models.IntegerField(verbose_name="Total Trades")

    def __str__(self):
        return '%d - %s' % (self.id, self.stock.symbol)


class StockProcessed(models.Model):
    stock_history = models.ForeignKey(StockHistory)
    created_at = models.DateField()
    deliverables = models.FloatField()
    watch_list = models.BooleanField(default=False)

    def __str__(self):
        return '%d - %s' % (self.id, self.stock_history.stock.symbol)
