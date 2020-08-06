import xml.etree.ElementTree as ET
import requests
import gzip
import urllib
from io import BytesIO
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

""" cursor.execute("SELECT * FROM database.scrape WHERE year=2002;")
results = cursor.fetchall()
for result in results:
    file_name = result[3]
    index_page = file_name.strip('.txt') + "-index.htm"
    accession_number = index_page.split('/')[8].strip('-index.htm')
    response = requests.get(index_page)
    soup = BeautifulSoup(response.content, 'lxml')
    report_period = soup.find('div', text='Period of Report')
    if report_period is None:
        continue
    report_period_year = report_period.find_next_sibling('div').text[0:4]
    if '2001' in report_period_year:
        cursor.execute("DELETE FROM database.scrape WHERE accession_number='%s';"%(accession_number))
    else:
        cursor.execute("UPDATE database.scrape SET year=%s WHERE accession_number='%s';"%(report_period_year, accession_number)) """

baseURL = r"https://www.sec.gov/Archives/edgar/daily-index/2014/QTR2/master.20140401.idx.gz"
response = urllib.request.urlopen(baseURL)
compressedFile = BytesIO(response.read())
decompressedFile = gzip.GzipFile(fileobj=compressedFile)
#print("decompressedFile is:", decompressedFile)
outfile = baseURL[57:-3]
with open(outfile, 'wb') as f:
    #f.write(decompressedFile.read())
    f.write(decompressedFile.read())
