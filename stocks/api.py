import json
from datetime import date, timedelta
from dateutil import parser
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from stocks.models import StockHistory, Stock
from django.conf import settings

import requests


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


@csrf_exempt
def watchlist_add(request):
    history_id = json.loads(request.body).get('row_id')
    comment = json.loads(request.body).get('comments')
    stock_qs = StockHistory.objects.filter(id=history_id)
    stock_qs.update(watch_list=True, comments=comment)
    return JsonResponse({})


def list_symbols(request):
    symbols = list(Stock.objects.all().values_list('symbol', flat=True))
    return JsonResponse({'symbols': symbols})


def stock_quotes(request):
    stock_ids = map(lambda x: int(x) if x else 0, request.GET['stock_ids'].split(','))
    symbols = Stock.objects.filter(id__in=stock_ids).values_list('symbol', flat=True)
    quotes_url = settings.STOCK_QUOTE_URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Referer': 'https://www.nseindia.com/live_market/dynaContent/live_watch/equities_stock_watch.htm'}

    results = []
    for x in range(0, len(symbols), 5):
        symbols_str = ','.join(symbols[x:x + 5])
        data = requests.get(quotes_url + '?symbol=' + symbols_str, headers=headers).json()['data']
        results.extend(data)
    return JsonResponse({'data': results})
