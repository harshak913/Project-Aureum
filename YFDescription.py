import psycopg2
import os
import sys
import csv
import bs4
import urllib3
import pdb
import requests # this is for price retrieving
import datetime
import time



#reload(sys)
#sys.setdefaultencoding('utf8')

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

total = 0
complete = 0
incomplete = 0
#For each company in the table collect the ticker
for entry in entries:
    ticker = entry[1]
    total +=1
    url3 = "https://finance.yahoo.com/quote/{0}/profile?p={0}".format(ticker)
#######This section is to get the Profile page's Description Info
    res = requests.get(url3)
#    print('line 122 res and ticker is',ticker, res)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    elems = soup.find("p","Mt(15px) Lh(1.6)")
#    print(' line 124 elems is:',soup, elems)

##### elems.string is string. Sometimes Yahoo Finance's URL does not have any data.
##### To avoid early exit from the rest of ticker files, we add this if statement to handle the situation
    if(bool(elems) and bool(elems.string)):
#    print('ticker, cash_yr and type bool()is:',ticker, cash_yr, type(cash_yr),bool(cash_yr))
        Description = elems.string
        print(ticker,'Line 132 Company Description is ', elems.string)
        complete+=1
    else:
        print('line 134 ticker, elems,string is empty', ticker)
        incomplete+=1
        continue

"""
UPDATE company SET description = '%s' WHERE ticker = '%s';

"""
    #stock_info_arr.append(stock_info)

'''
########## WRITING OUR RESULTS INTO EXCEL
#print('key_stats_on_main before extend is:',key_stats_on_main)
key_stats_on_main.append('Company Description')
#print('key_stats_on_main is: ', key_stats_on_main)

#### Now add a worksheet called Summary at the beginning

worksheet = workbook.add_worksheet('Summary')
worksheet.freeze_panes(1, 1)

row = 1
col = 0

for stat in key_stats_on_main:
    print('stat to be written to Excel is', stat)
    worksheet.write(row, col, stat)
    row +=1

row = 0
col = 1
for our_stock in stock_info_arr:
    row = 0
    for info_bit in our_stock:
        info_bit=str(info_bit)
        #print('line 138 info_bit to be written into Excel is:', info_bit)
        worksheet.write(row, col, info_bit)
        row += 1
    col += 1

workbook.close()

print('Script completed')
t2 = time.time()
print ('Total Time taken:')
print (t2-t1)
'''
