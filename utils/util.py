import requests, urllib
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
    base_url = settings.TELEGRAM_BASE_URL
    kaathi_id = settings.KAATHI_TELEGRAM_ID
    mani_id = settings.MANI_TELEGRAM_ID

    text_encode = urllib.quote_plus(text)
    url_kaathi = base_url + kaathi_id + "&text=" + text_encode
    url_mani = base_url + mani_id + "&text=" + text_encode

    resp_kaathi = requests.get(url=url_kaathi)
    resp_mani = requests.get(url=url_mani)


class NiftyStocks(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Referer': 'https://www.nseindia.com/live_market/dynaContent/live_watch/equities_stock_watch.htm'}

    def _get_from_source(self, url):
        data = requests.get(url, headers=self.headers)
        return data.json()

    def nifty(self):
        nifty_url = settings.NIFTY_URL
        return self._get_from_source(nifty_url)

    def next_nifty(self):
        next_nifty_url = settings.NEXT_NIFTY_URL
        return self._get_from_source(next_nifty_url)
