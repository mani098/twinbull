from datetime import date, timedelta, datetime
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
            trade_date = request.POST.get('trade-date')
            date_field = datetime.strptime(trade_date, '%m/%d/%Y').date() if trade_date else None
            symbol = request.POST.get('stock_symbol')
            if symbol:
                if not trade_date:
                    today_date = date.today()
                    stocks = stocks_qs.filter(trade_date__range=[today_date - timedelta(25), today_date],
                                              stock__symbol=symbol.strip()) \
                        .order_by('-trade_date')
                else:
                    stocks = stocks_qs.filter(trade_date=date_field, stock__symbol=symbol.strip())
            elif trade_date:
                stocks = stocks_qs.filter(trade_date=date_field).annotate(
                    change=F('close') - F('open')).select_related('stock')
            ctx['stocks'] = stocks

    elif request.method == 'GET':
        trade_date = stocks_qs.order_by('-trade_date').first().trade_date
        stocks = stocks_qs.filter(trade_date=trade_date)
        ctx['stocks'] = stocks

    return render(request, watch_list_template, ctx)
