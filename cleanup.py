import requests
import urllib
import datetime
import os
import re
from bs4 import BeautifulSoup
import psycopg2
import xml.etree.ElementTree as ET
from Inter_Table import interParse

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

cursor.execute("SELECT cik FROM database.company;")
ciks = cursor.fetchall()

years = list(range(2016, 2017))

""" cursor.execute("SELECT * FROM database.scrape WHERE year=2016;")
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
    cursor.execute("UPDATE database.scrape SET year=%s WHERE accession_number='%s';"%(report_period_year, accession_number)) """

for year in years:
    for cik in ciks:
        cursor.execute("SELECT * FROM database.scrape WHERE cik_id=%s AND year=%s;"%(cik[0], year))
        results = cursor.fetchall() # Sequence of tuples inside a list for each CIK (each tuple is info from scrape table for a filing)
        num10K = num10KFound = num10Q = num10QFound = 0
        for result in results:
            if result[1] == '10-K':
                num10K += 1
            elif result[1] == '10-Q':
                num10Q += 1
        dateb = str(year+1)+"0301"
        if num10K < 1:
            search_page = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=%s&dateb=%s&owner=exclude&count=40&search_text="%(cik[0], "10-K", dateb)
            response = requests.get(search_page)
            soup = BeautifulSoup(response.content, 'lxml')
            tenKName = soup.find('th', text=re.compile("File/Film Number")).find_next('td', text="10-K")
            while tenKName is not None and num10KFound < 1:
                if str(year) in tenKName.find_next('td').find_next('td').find_next('td').get_text() or str(year+1) in tenKName.find_next('td').find_next('td').find_next('td').get_text():
                    tenKLink = tenKName.find_next('td').find_next('a')['href']
                    accession_number = tenKLink.split('/')[6].strip('-index.htm')
                    indexLink = "https://www.sec.gov" + tenKLink
                    response = requests.get(indexLink)
                    soup = BeautifulSoup(response.content, 'lxml')
                    if str(year+1) in tenKName.find_next('td').find_next('td').find_next('td').get_text():
                        report_period = soup.find('div', text='Period of Report').find_next_sibling('div').text
                        if str(year) in report_period:
                            num10KFound = 1
                            print(indexLink) # Replace with interParse surrounded by try-except
                        else:
                            tenKName = tenKName.find_next('tr').find_next('td', text="10-K")
                            continue
                    elif str(year) in tenKName.find_next('td').find_next('td').find_next('td').get_text():
                        num10KFound = 1
                        report_period = soup.find('div', text='Period of Report').find_next_sibling('div').text
                        if str(year) in report_period:
                            num10KFound = 1
                            print(indexLink) # Replace with interParse surrounded by try-except
        """ if num10Q < 3:
            search_page = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=%s&dateb=%s&owner=exclude&count=40&search_text="%(cik[0], "10-Q", dateb)
            print(search_page)
            response = requests.get(search_page)
            soup = BeautifulSoup(response.content, 'lxml')
            tenQName = soup.find('th', text=re.compile("File/Film Number")).find_next('td', text="10-Q")
            while tenQName is not None and num10QFound < 3:
                if str(year) in tenQName.find_next('td').find_next('td').find_next('td').get_text():
                    tenQLink = tenQName.find_next('td').find_next('a')['href']
                    accession_number = tenQLink.split('/')[6].strip('-index.htm')
                    cursor.execute("SELECT * FROM database.scrape WHERE accession_number='%s'"%(accession_number))
                    if cursor.fetchone() is None:
                        print(type(cursor.fetchone()))
                    elif len(cursor.fetchone()) > 0:
                        tenQName = tenQName.find_next('tr').find_next('td', text="10-Q")
                        continue """

