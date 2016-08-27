from datetime import date, timedelta
from dateutil import parser
from django.http.response import JsonResponse

from stocks.models import StockHistory


def deliverableApi(request):
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
