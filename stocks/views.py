from django.shortcuts import render
from django.db.models import F
from .models import StockHistory


def index(request):
    index_template = 'stocks/index.html'

    stock_history = StockHistory.objects.filter(watch_list=True).select_related('stock').order_by('trade_date')

    return render(request, index_template, {'stocks': stock_history})


def stock_history_view(request):
    watch_list_template = 'stocks/history.html'
    if request.method == 'POST':

        if request.POST.get('search-btn'):
            date_field = request.POST.get('trade-date')
            stocks = StockHistory.objects.filter(trade_date=date_field, is_filtered=True).annotate(
                change=F('close') - F('open')).select_related('stock')

            if stocks:
                return render(request, watch_list_template, {'stocks': stocks})
            else:
                return render(request, watch_list_template)

        elif request.POST['to_watchlist']:
            watchlist_stocks = request.POST.getlist('watch_list')
            stocks = StockHistory.objects.filter(id__in=watchlist_stocks)
            stocks.update(watch_list=True)

            stocks_bydate = StockHistory.objects.filter(trade_date=stocks.first().trade_date, is_filtered=True).annotate(
                change=F('close') - F('open'))

            if stocks:
                return render(request, watch_list_template, {'stocks': stocks_bydate})
            else:
                return render(request, watch_list_template)

    else:
        return render(request, watch_list_template)


