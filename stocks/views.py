from django.shortcuts import render
from .models import Stock, StockHistory


def index(request):
    index_template = 'stocks/index.html'
    Watch_list = StockHistory.objects.filter(watch_list=True)

    return render(request, index_template, {'message': Watch_list})

def add_watch_list(request):
    watch_list_template = 'stocks/add.html'
    if request.method == 'POST':
        if request.POST['Button_clicked'] == 'Search':
            date_field = request.POST.get('dt')
            pending_stocks = StockHistory.objects.filter(watch_list=False, trade_date=date_field)

            if pending_stocks:
                return render(request, watch_list_template, {'mess': pending_stocks})
            else:
                return render(request, watch_list_template, {'mess': "No data is available"})

        elif request.POST['Button_clicked'] == 'add_to_watchlist':
            Tobe_added = request.POST.get('watch_list')
            Stock_to_be_added = StockHistory.objects.get(id=Tobe_added)
            print Stock_to_be_added.trade_date
            Stock_to_be_added.watch_list = True
            Stock_to_be_added.save()
            # return render(request, watch_list_template)

            pending_stocks = StockHistory.objects.filter(watch_list=False, trade_date=Stock_to_be_added.trade_date)

            if pending_stocks:
                return render(request, watch_list_template, {'mess': pending_stocks})
            else:
                return render(request, watch_list_template, {'mess': "No data is available"})


    else:
        return render(request, watch_list_template)