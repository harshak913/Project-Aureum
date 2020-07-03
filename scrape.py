import requests
import urllib
import datetime
import os
from bs4 import BeautifulSoup
import psycopg2
import xml.etree.ElementTree as ET


conn = psycopg2.connect(host="ec2-34-233-226-84.compute-1.amazonaws.com", dbname="d77knu57t1q9j9", user="jsnmfiqtcggjyu", password="368e05099543272efb167e9fa3173338be43c1e787666ed2478f51ef050707b9")
conn.autocommit = True
cursor = conn.cursor()

# Makes building a URL easy
def makeURL(baseURL, add):
    url = baseURL

    # Add each individual component to the base URL
    for i in add:
        url = '{}/{}'.format(url, i)
    return url

years = list(range(2002, 2003))

for year in years:
    
    # Define base URL to access daily filings
    baseURL = r"https://www.sec.gov/Archives/edgar/daily-index"

    # Choose .json as the format of the file we are pulling (only .json files have delimiters we can use for easy parsing)
    yearURL = makeURL(baseURL, [year, 'index.json'])
    JSONContent = requests.get(yearURL).json()

    for item in JSONContent['directory']['item']:

        # The daily-index filings require a year, a quarter, and content type (HTML, JSON, or XML)
        quarterURL = makeURL(baseURL, [year, item['name'], 'index.json'])
        QuarterJSONContent = requests.get(quarterURL).json()

        for file in QuarterJSONContent['directory']['item']:
            fileURL = makeURL(baseURL, [year, item['name'], file['name']])

            # Grab the Master IDX file URL
            if 'master' in fileURL:
                
                # Request that new content, this will NOT be a JSON STRUCTURE
                fileContent = requests.get(fileURL).content

                with open('master_file_text.txt', 'wb') as f:
                    f.write(fileContent)

                # We now have a byte stream of data
                with open('master_file_text.txt','r') as f:
                    byteData = f.readlines()
                
                os.remove('master_file_text.txt')

                headers = byteData[5].strip().split('|')
                headers = [header.lower().replace(' ','') for header in headers]
                fileData = byteData[7:]

                # We need to split the data into sections so we can get each row value
                for index in fileData:

                    # Clean it up.
                    index_split = index.strip().split('|')
                    if index_split[2] != '10-K' and index_split[2] != '10-Q':
                        continue
                    ciks = cursor.execute('''SELECT * FROM database.company WHERE cik=%s'''%(int(index_split[0])))
                    if len(cursor.fetchall()) < 1:
                        continue

                    # Create the URL
                    index_split_modify = index_split[4].split('/')
                    index_split[4] = ''
                    index_split_accession = ''.join(index_split_modify[3].strip('.txt').split('-'))
                    for x in index_split_modify[:-1]:
                        index_split[4] = index_split[4] + '/' + x
                    index_split[4] = index_split[4] + '/' + index_split_accession + '/' + index_split_modify[-1]
                    index_split[4] = "https://www.sec.gov/Archives" + index_split[4]

                    # Create the dictionary
                    filing_dict = dict(zip(headers, index_split))
                    text_filing = filing_dict['filename']
                    response = requests.get(text_filing)
                    soup = BeautifulSoup(response.content, 'lxml')
                    if len(soup.find_all('filename')) == 0:
                        continue
                    if '.htm' not in soup.find_all("filename")[0].get_text():
                        continue
                    accession_number = text_filing.split('/')[-1].strip('.txt') #Extract accession number (after last '/') & remove '.txt'
                    accession_exist = cursor.execute("SELECT * FROM database.scrape WHERE accession_number = '%s'"%(accession_number))
                    if len(cursor.fetchall()) > 0:
                        continue
                    url_list = text_filing.split('/')
                    url_xml = ''
                    for part in url_list[:-1]:
                        url_xml = url_xml + '' + part + '/'
                    url_xml = url_xml + 'FilingSummary.xml'
                    tree = ET.fromstring(requests.get(url_xml).text)
                    if 'NoSuchKey' in tree[0].text:
                        sql_statement = "INSERT INTO database.scrape (cik_id, filing_type, year, file_name, accession_number) VALUES(%s, '%s', %s, '%s', '%s');"%(int(filing_dict["cik"]), filing_dict["formtype"], filing_dict["datefiled"][0:4], filing_dict["filename"], accession_number)
                        cursor.execute(sql_statement)
                        print(sql_statement)