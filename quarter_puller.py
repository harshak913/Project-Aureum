import re
import urllib.request
from bs4 import BeautifulSoup, NavigableString
import os
import xml.etree.ElementTree as ET
import requests
import psycopg2
from datetime import datetime
from dateutil.relativedelta import relativedelta

#Database Connection
connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

filing_index = 'https://www.sec.gov/Archives/edgar/data/899689/000089968915000031/0000899689-15-000031-index.htm'

response = requests.get(filing_index)
soup = BeautifulSoup(response.content, 'lxml')
report_period = soup.find('div', text='Period of Report')
report_period = report_period.find_next_sibling('div').text
print('GOT THE FILING REPORT PERIOD')

#index portion
index = filing_index
result = index.split('/')
result = list(filter(None, result))
cik = int(result.index('data'))+1
cik = str(result[cik]) #CIK IS THE CIK NUMBER

print('WRITING THE INTERACTIVE PAGE')

#get interactive page link and save it as a file
latter = [i for i in result if '-index.htm' in i]
latter = str(''.join(latter))
latter = latter.replace('-index.htm', '') #LATTER IS THE UNIQUE ID FOR THE FILING
inter = 'https://www.sec.gov/cgi-bin/viewer?action=view&cik=%s&accession_number=%s&xbrl_type=v'%(cik,latter)
page = urllib.request.urlopen(inter).read()
soup = BeautifulSoup(page, features="lxml")
pretty = soup.prettify()
with open("%s.htm"%latter, "w") as file:
    file.write(pretty)

print('GETTING THE FINANCIAL STATEMENTS LINK')
financialStatementsFound = False
#CHECK THE INTERACTIVE PAGE AND GET THE NUMBER LINKS FOR NOTES AND FINANCIAL STATEMENTS
html = open("%s.htm"%latter).read()
soup = BeautifulSoup(html, features="lxml")
JS_Portion = soup.find("script", attrs={"type" : 'text/javascript' ,"language" : 'javascript'}).text
for element in soup.find_all('a'):
    if financialStatementsFound != True:
        if str(element.text).strip() == 'Cover' and element.find_next_sibling('ul') is not None:
            relevant = element.find_next_sibling('ul')
            dicts = []
            children = relevant.findChildren('a')
            financialStatementsFound = True
    else:
        break


for child in children:
    numbers = {}
    number = str(child['href'])
    number = number.replace('javascript:loadReport(', '')
    number = number.replace(');', '')
    numbers['number'] = str(number)
    numbers['name'] = str(child.text).strip()
    dicts.append(numbers)

print(dicts)

reports = []
#ASSEMBLE THE LIST OF ALL THE POSSIBLE LINKS TO THE ARCHIVE
for line in JS_Portion.split('\n'):
    if 'reports[' and '] = "/Archives/edgar/data/' in line:
        reports.append(line.strip())

print('matching correct report number with the correct dict')
#match correct report number with the correct dict
for report in reports:
    comp = report.split('] = "/Archives/edgar/data/', 1)[0]
    comp = comp.replace('reports[', '')
    comp = str(eval(comp))
    for item in dicts:
        if item["number"] == comp:
            link = report.split('= "', 1)[1]
            item['link'] = link.replace('";', '')

for item in dicts:
    if 'htm' in item['link']:
        doc_name = str(item.get('name'))
        print('NOW PARSING '+doc_name+ ' (A HTM DOC)')
        filename = "/Users/octavian/Desktop/HTM/%s.htm"%(doc_name)
        #filename = "/Users/Harsh/OneDrive - The University of Texas at Dallas/Documents/Project A/HTM/%s.htm"%(doc_name)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        report_access = 'https://www.sec.gov%s'%str(item.get('link'))
        page = requests.get(report_access)
        soup = BeautifulSoup(page.content, features="lxml")
        pretty = soup.prettify()
        with open(filename, "w") as f:
            f.write(pretty)
        htm = open(filename).read()
        soup = BeautifulSoup(htm , features="lxml")
        for element in soup.find('table').find_all('tr'):
            if element.find('td') is not None and element.find('td').text.strip() == 'Document Fiscal Period Focus':
                quarter = element.find('td').find_next_sibling('td').text.strip()

#use the quarter variable to insert into the scrape table as which quarter
