from datetime import date as python_date
from urllib.parse import quote_plus

import requests
from django.conf import settings
from urllib import parse as url_parse
from django.conf import settings


def calculate_charges(stock_price=0, quantity=0):
    """
    Calculate charges for equity delivery
    :param stock_price: <Float>
    :param quantity: <Int>
    :return: <Float>
    """

    traded_value = (stock_price * quantity) / 100

    brokerage = 0  # Zero brokerage for equity delivery
    stt = traded_value * 0.1  # 0.1 % for buy & sell
    transaction_charges = traded_value * 0.00325  # NSE: 0.00325%
    service_tax = ((brokerage + transaction_charges) / 100) * 15  # 15% on (brokerage + transaction charges)
    sebi_charges = 20  # Rs.20 per crore
    stamp_duty = traded_value * 0.01  # 0.01% - max Rs. 50
    if stamp_duty >= 50:
        stamp_duty = 50

    return brokerage + stt + transaction_charges + service_tax + sebi_charges + stamp_duty


def send_via_telegram(text):
    """Send message via telegram bot"""
    base_url = settings.TELEGRAM_BASE_URL
    # kaathi_id = settings.KAATHI_TELEGRAM_ID
    mani_id = settings.MANI_TELEGRAM_ID

    text_encode = quote_plus(text)
    # url_kaathi = base_url + kaathi_id + "&text=" + text_encode
    url_mani = base_url + mani_id + "&text=" + text_encode

    # resp_kaathi = requests.get(url=url_kaathi)
    resp_mani = requests.get(url=url_mani)


class NiftyStocks(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Referer': 'https://www.nseindia.com/live_market/dynaContent/live_watch/equities_stock_watch.htm',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, sdch, br'}

    def _get_from_source(self, url):
        data = requests.get(url, headers=self.headers)
        return data.json()

    def nifty(self):
        nifty_url = settings.NIFTY_URL
        return self._get_from_source(nifty_url)

    def next_nifty(self):
        next_nifty_url = settings.NEXT_NIFTY_URL
        return self._get_from_source(next_nifty_url)


class NseHelper(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Referer': 'https://www.nseindia.com/live_market/dynaContent/live_watch/equities_stock_watch.htm'}

    def stock_quotes(self, symbols):
        quotes_url = settings.STOCK_QUOTE_URL
        results = []
        for x in range(0, len(symbols), 5):
            symbols_str = ','.join(map(lambda i: url_parse.quote(i), symbols[x:x + 5]))
            data = requests.get(quotes_url + '?symbol=' + symbols_str, headers=self.headers).json()['data']
            results.extend(data)
        return results


def get_quarter_month(date):
    """Returns the quarter's first month by the given date"""
    quarter_month_map = {1: 1, 2: 4, 3: 6, 4: 8}
    assert isinstance(date, python_date), "Field must be date type"
    return quarter_month_map[((date.month - 1) // 3 + 1)]  # Eg: 1 for Jan, 4 for april
