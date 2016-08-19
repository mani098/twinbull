from django.shortcuts import render
from django.db.models import F
from .models import StockHistory


def index(request):
    index_template = 'stocks/index.html'
    stock_history = StockHistory.objects.filter(watch_list=True)

    return render(request, index_template, {'stocks': stock_history})


def stock_history_view(request):
    watch_list_template = 'stocks/history.html'
    if request.POST:
        date_field = request.POST.get('trade-date')
        stocks = StockHistory.objects.filter(watch_list=False, trade_date=date_field).annotate(change=F('close') - F('open'))
        return render(request, watch_list_template, {'stocks': stocks})
    else:
        return render(request, watch_list_template)