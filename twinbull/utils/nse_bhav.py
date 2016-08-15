import requests
import zipfile
import json
from BeautifulSoup import BeautifulSoup

class Nse(object):

    def __init__(self, trade_date):
        self.trade_date = trade_date
        self.trade_date=self.trade_date.split('-')

    def get_data(self):
        date_dict = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
                     '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
                     '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}

        bhavcopy_url = 'https://www.nseindia.com/content/historical/EQUITIES/%s/%s/cm%s%s%sbhav.csv.zip' % (self.trade_date[0], date_dict[self.trade_date[1]],
                                                                                                            self.trade_date[2], date_dict[self.trade_date[1]],
                                                                                                            self.trade_date[0])
        response = requests.get(bhavcopy_url, stream=True)

        if response.status_code == 200:
            f = open("/tmp/bhav.csv.zip",'wb')
            f.write(response.content)
            f.close()
            return self.read_zip_file('/tmp/bhav.csv.zip')
        else:
            print "sorry!, no records available"
            return 

    def read_zip_file(self, filepath):
        stock_list = []
        zfile = zipfile.ZipFile(filepath)

        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            stocks =  ifile.readlines()
            for stock in stocks:
                stock_data = stock.split(',')
                
                if stock_data[1] == 'EQ':
                    dictionary = {'SYMBOL':stock_data[0],
                                  'OPEN':float(stock_data[2]),
                                  'HIGH':float(stock_data[3]),
                                  'LOW':float(stock_data[4]),
                                  'CLOSE':float(stock_data[5]),
                                  'LAST':float(stock_data[6]),
                                  'PREVCLOSE':float(stock_data[7]),
                                  'TOTTRDQTY':stock_data[8],
                                  'TOTTRDVAL':float(stock_data[9]),
                                  'TRADEDDATE':stock_data[10],
                                  'TOTALTRADES':stock_data[11],
                                  'ISIN':stock_data[12]}
                    stock_list.append(dictionary)

        return stock_list

    def deliverables(self, symbol):

        r = requests.get("https://nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol=%s" %symbol)
        soup = BeautifulSoup(r.text)
        json_data = json.loads(soup.find(id='responseDiv').text)

        stock_deliverables = json_data['data'][0]['deliveryToTradedQuantity']
        return stock_deliverables



