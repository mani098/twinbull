import json
from datetime import date, timedelta
from dateutil import parser
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from stocks.models import StockHistory


def deliverable_api(request):
    symbol = request.GET.get('symbol')
    trade_date, to_date = request.GET.get('trade_date'), request.GET.get('to_date', date.today())
    trade_date = parser.parse(trade_date).date()
    from_date = trade_date - timedelta(20)
    if not isinstance(to_date, date):
        to_date = parser.parse(to_date).date()
    stocks_data = list(StockHistory.objects.filter(stock__symbol=symbol, trade_date__range=[from_date, to_date]).values(
        'trade_date', 'deliverables', 'close', 'total_traded_qty').order_by('trade_date'))
    response_data = {'data': stocks_data}
    return JsonResponse(response_data)


@csrf_exempt
def watchlist_remove(request):
    history_id = json.loads(request.body).get('row_id')
    stock_qs = StockHistory.objects.filter(id=history_id)
    stock_qs.update(watch_list=False)
    return JsonResponse({})
