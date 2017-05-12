from datetime import datetime

from django.shortcuts import render
from django.views import View

from .models import StockOrder


class IndexView(View):
    template_name = 'stocks/index.html'

    def get(self, request):
        _trade_date = request.GET.get('trade-date')
        trade_date = datetime.strptime(_trade_date, '%m/%d/%Y').date() if _trade_date else StockOrder.objects.\
            latest('trade_date').trade_date
        stock_orders = StockOrder.objects.select_related('stock_history', 'stock_history__stock'). \
            filter(created_at__date=trade_date)

        return render(request, self.template_name, {'stocks': stock_orders})
