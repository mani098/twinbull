import requests
import zipfile
import json
from BeautifulSoup import BeautifulSoup

class Nse(object):

    def __init__(self, trade_date):
        self.trade_date = trade_date


    def get_data(self):
        response = requests.get('https://www.nseindia.com/content/historical/EQUITIES/2016/AUG/cm12AUG2016bhav.csv.zip', stream=True)
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
                    dictionary = {'SYMBOL':stock_data[0], 'OPEN':float(stock_data[2]), 'HIGH':float(stock_data[3]), 'LOW':float(stock_data[4]), 
                                  'CLOSE':float(stock_data[5]), 'LAST':float(stock_data[6]), 'PREVCLOSE':float(stock_data[7]), 'TOTTRDQTY':stock_data[8],
                                  'TOTTRDVAL':float(stock_data[9]), 'TOTALTRADES':stock_data[10], 'ISIN':stock_data[11]}
                    stock_list.append(dictionary)

        return stock_list

    def deliverables(self, symbol):

        r = requests.get("https://nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol=%s" %symbol)
        soup = BeautifulSoup(r.text)
        json_data = json.loads(soup.find(id='responseDiv').text)

        stock_deliverables = json_data['data'][0]['deliveryToTradedQuantity']
        return stock_deliverables



