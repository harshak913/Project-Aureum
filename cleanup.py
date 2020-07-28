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

""" cursor.execute("SELECT accession_number FROM database.scrape WHERE year=2016;")
accessions = cursor.fetchall()

for accession in accessions:
    cursor.execute("SELECT * FROM database.balance WHERE accession_number='%s';"%(accession[0]))
    balance_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM database.income WHERE accession_number='%s';"%(accession[0]))
    income_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM database.cash_flow WHERE accession_number='%s';"%(accession[0]))
    cash_flow_entry = cursor.fetchall()

    if len(balance_entry) == 0 or len(income_entry) == 0 or len(cash_flow_entry) == 0:
        cursor.execute("UPDATE database.scrape SET status='INCOMPLETE' WHERE accession_number='%s';"%(accession[0]))
    else:
        cursor.execute("UPDATE database.scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession[0])) """

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

# Select all company CIKs
cursor.execute("SELECT cik FROM database.company;")
ciks = cursor.fetchall()

years = list(range(2016, 2017))

for year in years:
    for cik in ciks:
        cursor.execute("SELECT * FROM database.scrape WHERE cik_id=%s AND year=%s;"%(cik[0], year))
        results = cursor.fetchall() # Sequence of tuples inside a list for each CIK (each tuple is info from scrape table for a filing)
        num10K = num10KFound = num10Q = num10QFound = 0

        # Record number of 10Ks & 10-Qs present in the database right now
        for result in results:
            if result[1] == '10-K':
                num10K += 1
            elif result[1] == '10-Q':
                num10Q += 1
        
        dateb = str(year+1)+"0329"
        if num10K < 1: #If we have no 10-Ks present for this CIK and year, then parse the Edgar search page
            search_page = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=%s&dateb=%s&owner=exclude&count=40&search_text="%(cik[0], "10-K", dateb) # Go to the search page for that specific CIK and filing type
            response = requests.get(search_page)
            soup = BeautifulSoup(response.content, 'lxml')
            tenKName = soup.find('th', text=re.compile("File/Film Number")).find_next('td', text="10-K")

            # Keeps running as long as valid search results exist or no 10-Ks have been found
            while tenKName is not None and num10KFound < 1:

                # Hitting the previous year means we've looked at all possible missing 10-Ks
                if str(year-1) in tenKName.find_next('td').find_next('td').find_next('td').get_text():
                    break
                # Only check the current and next year for possible missing 10-Ks
                elif str(year) in tenKName.find_next('td').find_next('td').find_next('td').get_text() or str(year+1) in tenKName.find_next('td').find_next('td').find_next('td').get_text():
                    tenKLink = tenKName.find_next('td').find_next('a')['href']
                    accession_number = tenKLink.split('/')[6].strip('-index.htm')
                    indexLink = "https://www.sec.gov" + tenKLink
                    soup = BeautifulSoup(requests.get(indexLink).content, 'lxml')

                    # Check period of report for the next year
                    if str(year+1) in tenKName.find_next('td').find_next('td').find_next('td').get_text():
                        report_period = soup.find('div', text='Period of Report').find_next_sibling('div').text

                        #If the current year is in the period of report, then parse it and increment num10KFound
                        if str(year) in report_period:
                            num10KFound = 1
                            print(indexLink) # Replace with interParse surrounded by try-except
                        else:
                            if tenKName.find_next('tr') is not None:
                                tenKName = tenKName.find_next('tr').find_next('td', text="10-K")
                                continue
                            else:
                                break
                    
                    # Check period of report for the current year
                    elif str(year) in tenKName.find_next('td').find_next('td').find_next('td').get_text():
                        report_period = soup.find('div', text='Period of Report').find_next_sibling('div').text

                        #If the current year is in the period of report, then parse it and increment num10KFound
                        if str(year) in report_period:
                            num10KFound = 1
                            print(indexLink) # Replace with interParse surrounded by try-except
        

        if num10Q < 3: #If we have less than 3 10-Qs present for this CIK and year, then parse the Edgar search page
            search_page = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=%s&dateb=%s&owner=exclude&count=40&search_text="%(cik[0], "10-Q", dateb)
            print(search_page)
            response = requests.get(search_page)
            soup = BeautifulSoup(response.content, 'lxml')
            tenQName = soup.find('th', text=re.compile("File/Film Number")).find_next('td', text="10-Q")

            # Keeps running as long as valid search results exist or less than 3 10-Qs have been found
            while tenQName is not None and num10QFound < 3:

                # Hitting the previous year means we've looked at all possible missing 10-Qs
                if str(year-1) in tenQName.find_next('td').find_next('td').find_next('td').get_text():
                    break
                # Only check the current and next year for possible missing 10-Qs
                elif str(year) in tenQName.find_next('td').find_next('td').find_next('td').get_text() or str(year+1) in tenQName.find_next('td').find_next('td').find_next('td').get_text():
                    tenQLink = tenQName.find_next('td').find_next('a')['href']
                    accession_number = tenQLink.split('/')[6].strip('-index.htm')
                    indexLink = "https://www.sec.gov" + tenQLink
                    soup = BeautifulSoup(requests.get(indexLink).content, 'lxml')
                    cursor.execute("SELECT * FROM database.scrape WHERE accession_number='%s'"%(accession_number))
                    result = cursor.fetchone()

                    # If the current accession number DOES NOT exist in the scrape table, then look at its period of report
                    if len(result) == 0:
                        # Check period of report for the current year
                        if str(year) in tenQName.find_next('td').find_next('td').find_next('td').get_text():
                            report_period = soup.find('div', text='Period of Report').find_next_sibling('div').text

                            #If the current year is in the period of report, then parse it and increment num10QFound
                            if str(year) in report_period:
                                num10QFound += 1
                                print(indexLink) # Replace with interParse surrounded by try-except
                        
                        # Check period of report for the next year
                        elif str(year+1) in tenQName.find_next('td').find_next('td').find_next('td').get_text():
                            report_period = soup.find('div', text='Period of Report').find_next_sibling('div').text

                            #If the current year is in the period of report, then parse it and increment num10QFound
                            if str(year) in report_period:
                                num10QFound += 1
                                print(indexLink) # Replace with interParse surrounded by try-except
                        if tenQName.find_next('tr') is not None:
                            tenQName = tenQName.find_next('tr').find_next('td', text="10-Q")
                        else:
                            break

                    # If the current accession number exists in the scrape table, then increment num10QFound and go to the next search result
                    elif len(result) > 0:
                        num10QFound += 1
                        if tenQName.find_next('tr') is not None:
                            tenQName = tenQName.find_next('tr').find_next('td', text="10-Q")
                        else:
                            break