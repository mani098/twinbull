from datetime import date
from django.db.models import F
from django.shortcuts import render

from .models import StockHistory


def index(request):
    index_template = 'stocks/index.html'
    stock_history = StockHistory.objects.filter(watch_list=True).select_related('stock').order_by('trade_date')

    return render(request, index_template, {'stocks': stock_history})


def stock_history_view(request):
    watch_list_template = 'stocks/history.html'
    ctx = {'stocks': []}
    if request.method == 'POST':
        if request.POST.get('search-btn'):
            date_field = request.POST.get('trade-date') or date.today()
            symbol = request.POST.get('stock_symbol')
            if symbol:
                stocks = StockHistory.objects.filter(trade_date=date_field, stock__symbol=symbol.strip())
            else:
                stocks = StockHistory.objects.filter(trade_date=date_field, is_filtered=True).annotate(
                    change=F('close') - F('open')).select_related('stock')
            ctx['stocks'] = stocks

        elif request.POST.get('to_watchlist'):
            watchlist_stocks = request.POST.getlist('watch_list')
            stocks = StockHistory.objects.filter(id__in=watchlist_stocks)
            stocks.update(watch_list=True)

            stocks_bydate = StockHistory.objects.filter(trade_date=stocks.first().trade_date,
                                                        is_filtered=True).annotate(
                change=F('close') - F('open'))

            ctx['stocks'] = stocks_bydate

    return render(request, watch_list_template, ctx)
