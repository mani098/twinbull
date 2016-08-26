from django.http.response import JsonResponse
from stocks.models import StockHistory
from datetime import date
from dateutil import parser


def deliverableApi(request):
    symbol = request.GET.get('symbol')
    from_date, to_date = request.GET.get('from_date'), request.GET.get('to_date', date.today())
    from_date = parser.parse(from_date).date()
    if not isinstance(to_date, date):
        to_date = parser.parse(to_date).date()
    stocks_data = list(StockHistory.objects.filter(stock__symbol=symbol, trade_date__range=[from_date, to_date]).values(
        'trade_date', 'deliverables', 'close', 'total_traded_qty').order_by('trade_date'))
    response_data = {'data': stocks_data}
    return JsonResponse(response_data)
