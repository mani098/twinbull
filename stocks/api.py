from urllib import parse as url_parse

import requests
from django.conf import settings
from django.http.response import JsonResponse

from stocks.models import Stock


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
        symbols_str = ','.join(map(lambda i: url_parse.quote(i), symbols[x:x + 5]))
        data = requests.get(quotes_url + '?symbol=' + symbols_str, headers=headers).json()['data']
        results.extend(data)
    return JsonResponse({'data': results})
