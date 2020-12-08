import psycopg2
import bs4
import urllib3
import re
import requests # this is for price retrieving
import unidecode
import unicodedata


#reload(sys)
#sys.setdefaultencoding('utf8')

def restore_windows_1252_characters(restore_string):
    def to_windows_1252(match):
        try:
            return bytes([ord(match.group(0))]).decode('cp1252')
        except UnicodeDecodeError:
            # No character at the corresponding code point: remove it.
            return ''
    return re.sub(r'[\u0080-\u0099]', to_windows_1252, restore_string)

key_stats_on_main =[]
key_stats_on_stat =['Enterprise Value', 'Trailing P/E', 'Forward P/E',
                     'PEG Ratio (5 yr expected)', 'Price/Sales','Price/Book',
                     'Enterprise Value/Revenue','Enterprise Value/EBITDA',
                     'Fiscal Year Ends','Most Recent Quarter',
                     'Profit Margin','Operating Margin','Return on Assets', 'Return on Equity',
                     'Revenue','Revenue Per Share','Quarterly Revenue Growth','Gross Profit',
                     'EBITDA', 'Net Income Avi to Common','Diluted EPS','Quarterly Earnings Growth',
                     'Total Cash','Total Cash Per Share','Total Debt','Total Debt/Equity', 'Current Ratio', 'Book Value Per Share',
                     'Operating Cash Flow','Levered Free Cash Flow','Beta','52-Week Change','S&P500 52-Week Change',
                     '52 Week High','52 Week Low','50-Day Moving Average','200-Day Moving Average',
                     'Avg Vol (3 month)','Avg Vol (10 day)','Shares Outstanding','Float','% Held by Insiders',
                     '% Held by Institutions',
                     'Forward Annual Dividend Rate','Forward Annual Dividend Yield',
                     'Trailing Annual Dividend Rate','Trailing Annual Dividend Yield','5 Year Average Dividend Yield',
                     'Payout Ratio','Dividend Date','Ex-Dividend Date']
key_stats_on_profile =['Description']

'''
t1 = time.time()

now = datetime.datetime.now()
datetag = now.strftime("%Y-%m-%d-%H-%M")
######Open the File to be written
#outputfilename =  "YF2tab-" + datetag + "-" + timetag + ".xlsx"
outputfilename =  "YFDescription-" + datetag + ".xlsx"
workbook = xlsxwriter.Workbook(outputfilename)

stocks_arr =[]
pfolio_file= open("stocks-Master.csv", "r")
for line in pfolio_file:
    indv_stock_arr = line.strip().split(',')
    stocks_arr.append(indv_stock_arr)
'''

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

scrape_query = "select * from company;"
cursor.execute(scrape_query)
entries = cursor.fetchall()

#Collect
for entry in entries:
    print(entry[1])

#For each company in the table collect the ticker
for entry in entries:
    ticker = entry[1]
    url3 = "https://finance.yahoo.com/quote/{0}/profile?p={0}".format(ticker)
#######This section is to get the Profile page's Description Info
    res = requests.get(url3)
#    print('line 122 res and ticker is',ticker, res)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    elems = soup.find("p", attrs = {"class":"Mt(15px) Lh(1.6)"})
#    print(' line 124 elems is:',soup, elems)

##### elems.string is string. Sometimes Yahoo Finance's URL does not have any data.
##### To avoid early exit from the rest of ticker files, we add this if statement to handle the situation
    if(bool(elems) and bool(elems.string)):
#    print('ticker, cash_yr and type bool()is:',ticker, cash_yr, type(cash_yr),bool(cash_yr))
        description = unidecode.unidecode(restore_windows_1252_characters(unicodedata.normalize('NFKD', elems.string.decode('utf-8')))).replace("'", "''")
        cursor.execute("UPDATE company SET description = '%s' WHERE ticker = '%s';"%(description, ticker))