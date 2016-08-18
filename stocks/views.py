from django.shortcuts import render
from .models import Stock, StockHistory


def index(request):
    index_template = 'stocks/index.html'
    a = StockHistory.objects.filter(watch_list=True)

    return render(request, index_template, {'mess': a})

def add_watch_list(request):
    watch_list_template = 'stocks/add.html'
    if request.POST:
        date_field = request.POST.get('dt')
        b = StockHistory.objects.filter(watch_list=False, trade_date=date_field)

        if b:
            return render(request, watch_list_template, {'mess': b})
        else:
            return render(request, watch_list_template, {'mess': "No data is available"})
    else:
        return render(request, watch_list_template)