import requests
from edgar import Edgar
from bs4 import BeautifulSoup
import psycopg2

edgar = Edgar()

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="DB^oo^ec@^h@ckth!$0913")
conn.autocommit = True
cursor = conn.cursor()

sp500_tickers = []
sp500_url = 'https://www.slickcharts.com/sp500'
sp_response = requests.get(sp500_url)
sp_soup = BeautifulSoup(sp_response.content, 'lxml')
for tr in sp_soup.find_all('tr'):
    if len(tr.find_all('td')) == 0:
        continue
    td = tr.find_all('td')[2].get_text()
    if '.' in td:
        td = td.replace('.', '-')
    sp500_tickers.append(td)

with open("C:/Users/Harsh/OneDrive - The University of Texas at Dallas/Documents/Project A/Project-Aureum/SECDataCollection/cik_ticker.txt", "r") as file:
    lines = file.readlines()
    company_dataset = []
    header = ['cik', 'ticker', 'name', 'classification']
    for line in lines:
        index = line.strip().split('\t')
        ticker = index[0].upper()
        try:
            ticker_index = sp500_tickers.index(ticker)
            cik_length = len(index[1])
            cik = ''
            for i in range(10-cik_length):
                cik = cik + '0'
            cik = cik + index[1]
            name = edgar.get_company_name_by_cik(cik)
            url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=%s&action=getcompany&owner=exclude'%(ticker)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'lxml')
            sic_tag = soup.find('acronym', text='SIC')
            if sic_tag is not None:
                sic = sic_tag.find_next('a').get_text() + sic_tag.find_next('a').find_next('br').get_text()
            else:
                sic = ''
            if soup.find('p', {'class' : 'identInfo'}) is None:
                continue
            if 'formerly' in soup.find('p', {'class' : 'identInfo'}).get_text():
                name = ''
                updated_name_list = soup.find('span', {'class' : 'companyName'}).get_text().split()
                for index in range(len(updated_name_list)):
                    if 'CIK' in updated_name_list[index]:
                        break
                    if index == 0:
                        name = updated_name_list[index]
                    else:
                        name = name + ' ' + updated_name_list[index]
            name = name.replace("'", "''")
            sql_statement = "INSERT INTO company(cik, ticker, name, classification) VALUES(%s, '%s', '%s', '%s');"%(cik, ticker, name.upper(), sic)
            rows = cursor.execute('''SELECT * FROM company WHERE cik=%s;'''%(cik))
            if len(cursor.fetchall()) < 1:
                cursor.execute(sql_statement)
        except ValueError:
            continue