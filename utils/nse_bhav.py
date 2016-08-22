import logging
import zipfile
from datetime import datetime

import requests
from django.conf import settings

BHAV_COPY_URL = settings.BHAV_COPY_URL
DELIVERABLES_URL = settings.DELIVERABLES_URL
BHAV_LOCAL_PATH = settings.BHAV_LOCAL_PATH

logger = logging.getLogger(__name__)


class Nse(object):

    def __init__(self, trade_date):
        self.trade_date = trade_date

    def deliverables_data(self):
        data = {}
        trade_date = self.trade_date.strftime('%d%m%Y')
        deliverables_url = DELIVERABLES_URL % trade_date
        response = requests.get(deliverables_url, stream=True)
        if response.status_code == 200:
            data_dat = response.content
            deliverables_data = data_dat.split('\n')[4:]
            for i in deliverables_data:
                stock = i.split(',')
                try:
                    if stock[3] == 'EQ':
                        symbol = stock[2]
                        deliverables = stock[6]
                        data[symbol] = deliverables
                except IndexError:
                    pass
        return data

    def data(self):
        trade_date = self.trade_date.isoformat()
        trade_date = trade_date.split('-')

        date_dict = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
                     '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
                     '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}

        bhavcopy_url = BHAV_COPY_URL % (trade_date[0], date_dict[trade_date[1]],
                                        trade_date[2], date_dict[trade_date[1]],
                                        trade_date[0])

        response = requests.get(bhavcopy_url, stream=True)
        if response.status_code == 200:
            f = open(BHAV_LOCAL_PATH, 'wb')
            f.write(response.content)
            f.close()
            return self._read_zip_file(BHAV_LOCAL_PATH)
        else:
            print "sorry!, no records available"
            return []

    def _read_zip_file(self, filepath):
        zfile = zipfile.ZipFile(filepath)
        deliverables_data = self.deliverables_data()

        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            stocks = ifile.readlines()
            for i, stock in enumerate(stocks):
                stock_data = stock.split(',')
                if stock_data[1] == 'EQ':
                    trade_date = datetime.strptime(stock_data[10], '%d-%b-%Y').date()
                    stock_hash = {'SYMBOL':      stock_data[0],
                                  'OPEN':        float(stock_data[2]),
                                  'HIGH':        float(stock_data[3]),
                                  'LOW':         float(stock_data[4]),
                                  'CLOSE':       float(stock_data[5]),
                                  'LAST':        float(stock_data[6]),
                                  'PREVCLOSE':   float(stock_data[7]),
                                  'TOTTRDQTY':   int(stock_data[8]),
                                  'TOTTRDVAL':   float(stock_data[9]),
                                  'TRADEDDATE':  trade_date,
                                  'TOTALTRADES': int(stock_data[11]),
                                  'DELIVERABLES': float(deliverables_data[stock_data[0]]),
                                  'ISIN':        stock_data[12]}
                    filtered_stock = self.filter_stock(stock=stock_hash)
                    yield filtered_stock

    def filter_stock(self, stock):
        today_change = stock['CLOSE'] - stock['OPEN']
        prev_change = stock['CLOSE'] - stock['PREVCLOSE']

        if 15 <= stock['CLOSE'] <= 1000 and stock['TOTTRDQTY'] >= 10000 and \
                (11 <= today_change <= 25 or -11 >= today_change >= -25) and \
                prev_change >= stock['PREVCLOSE']/100 and stock['DELIVERABLES'] > 65:

            stock.update({'is_filtered': True})
        else:
            stock.update({'is_filtered': False})

        return stock

