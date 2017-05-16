from urllib import parse as url_parse

import requests
from django.conf import settings
from django.http.response import JsonResponse

from stocks.models import Stock
from utils.util import NseHelper


def list_symbols(request):
    symbols = list(Stock.objects.all().values_list('symbol', flat=True))
    return JsonResponse({'symbols': symbols})


def stock_quotes(request):
    stock_ids = map(lambda x: int(x) if x else 0, request.GET['stock_ids'].split(','))
    symbols = Stock.objects.filter(id__in=stock_ids).values_list('symbol', flat=True)
    results = NseHelper().stock_quotes(symbols)
    return JsonResponse({'data': results})
