from django.shortcuts import render
from django.db.models import F
from .models import StockHistory


def index(request):
    index_template = 'stocks/index.html'

    stock_history = StockHistory.objects.filter(watch_list=True)

    return render(request, index_template, {'stocks': stock_history})


def stock_history_view(request):
    watch_list_template = 'stocks/history.html'
    if request.method == 'POST':
        if request.POST['Button_clicked'] == 'Search':
            date_field = request.POST.get('trade-date')
            stocks = StockHistory.objects.filter(trade_date=date_field).annotate(
                change=F('close') - F('open'))

            if stocks:
                return render(request, watch_list_template, {'stocks': stocks})
            else:
                return render(request, watch_list_template)

        elif request.POST['Button_clicked'] == 'add_to_watchlist':
            Tobe_added = request.POST.get('watch_list')
            Stock_to_be_added = StockHistory.objects.get(id=Tobe_added)
            print Stock_to_be_added.trade_date
            Stock_to_be_added.watch_list = True
            Stock_to_be_added.save()

            stocks = StockHistory.objects.filter(trade_date=Stock_to_be_added.trade_date).annotate(
                change=F('close') - F('open'))

            if stocks:
                return render(request, watch_list_template, {'stocks': stocks})
            else:
                return render(request, watch_list_template)

    else:
        return render(request, watch_list_template)


