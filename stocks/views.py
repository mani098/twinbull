from datetime import date, timedelta
from django.db.models import F
from django.shortcuts import render

from .models import StockHistory


def index(request):
    index_template = 'stocks/index.html'
    stock_history = StockHistory.objects.filter(watch_list=True).select_related('stock').order_by('-trade_date')

    return render(request, index_template, {'stocks': stock_history})


def stock_history_view(request):
    watch_list_template = 'stocks/history.html'
    ctx = {'stocks': []}
    stocks_qs = StockHistory.objects.filter(is_filtered=True)
    if request.method == 'POST':
        if request.POST.get('search-btn'):
            date_field = request.POST.get('trade-date')
            symbol = request.POST.get('stock_symbol')
            if symbol:
                if not date_field:
                    today_date = date.today()
                    stocks = stocks_qs.filter(trade_date__range=[today_date - timedelta(25), today_date],
                                              stock__symbol=symbol.strip()) \
                        .order_by('-trade_date')
                else:
                    stocks = stocks_qs.filter(trade_date=date_field, stock__symbol=symbol.strip())
            else:
                stocks = stocks_qs.filter(trade_date=date_field).annotate(
                    change=F('close') - F('open')).select_related('stock')
            ctx['stocks'] = stocks

        # elif request.POST.get('to_watchlist'):
        #     watchlist_stocks = request.POST.getlist('watch_list')
        #     stocks = StockHistory.objects.filter(id__in=watchlist_stocks)
        #     stocks.update(watch_list=True)
        #
        #     stocks_bydate = stocks_qs.filter(trade_date=stocks.first().trade_date) \
        #         .annotate(change=F('close') - F('open'))
        #
        #     ctx['stocks'] = stocks_bydate

    elif request.method == 'GET':
        trade_date = stocks_qs.order_by('-trade_date').first().trade_date
        stocks = stocks_qs.filter(trade_date=trade_date)
        ctx['stocks'] = stocks

        return render(request, watch_list_template, ctx)

    return render(request, watch_list_template, ctx)
