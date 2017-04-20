from datetime import date, timedelta, datetime
from django.core.urlresolvers import reverse
from django.db.models import F
from django.shortcuts import render, redirect
from django.views import View

from .models import StockHistory


class IndexView(View):
    template_name = 'stocks/index.html'

    def get(self, request):
        _trade_date = request.GET.get('trade-date')
        trade_date = datetime.strptime(_trade_date, '%m/%d/%Y').date() if _trade_date else StockHistory.objects.filter(
            watch_list=True).latest('trade_date').trade_date
        stock_history = StockHistory.objects.select_related('stock').filter(watch_list=True, trade_date=trade_date)

        return render(request, self.template_name, {'stocks': stock_history})


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

                    if not stocks:
                        stocks_nt_filt = StockHistory.objects.filter(is_filtered=False)
                        trade_date = stocks_nt_filt.order_by('-trade_date').first().trade_date
                        stocks = stocks_nt_filt.filter(trade_date=trade_date, stock__symbol=symbol)
                else:
                    stocks = stocks_qs.filter(trade_date=date_field, stock__symbol=symbol.strip())
            elif trade_date:
                stocks = stocks_qs.filter(trade_date=date_field).annotate(
                    change=F('close') - F('open')).select_related('stock')
            else:
                return redirect(reverse('history'))

            ctx['stocks'] = stocks

    elif request.method == 'GET':
        trade_date = stocks_qs.order_by('-trade_date').first().trade_date
        stocks = stocks_qs.filter(trade_date=trade_date)
        ctx['stocks'] = stocks

    return render(request, watch_list_template, ctx)
