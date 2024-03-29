import requests
import urllib
import os
import gzip
import urllib
from io import BytesIO
from bs4 import BeautifulSoup
import psycopg2
import xml.etree.ElementTree as ET
#from Inter_Table import interParse
import unidecode
import unicodedata
import re


connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

# Makes building a URL easy
def makeURL(baseURL, add):
    url = baseURL

    # Add each individual component to the base URL
    for i in add:
        url = '{}/{}'.format(url, i)
    return url

def restore_windows_1252_characters(restore_string):
    def to_windows_1252(match):
        try:
            return bytes([ord(match.group(0))]).decode('cp1252')
        except UnicodeDecodeError:
            # No character at the corresponding code point: remove it.
            return ''
    return re.sub(r'[\u0080-\u0099]', to_windows_1252, restore_string)

def delete_from_tables(accession_number):
    cursor.execute("DELETE FROM balance WHERE accession_number='%s';"%(accession_number))
    cursor.execute("DELETE FROM income WHERE accession_number='%s';"%(accession_number))
    cursor.execute("DELETE FROM cash_flow WHERE accession_number='%s';"%(accession_number))
    cursor.execute("DELETE FROM non_statement WHERE accession_number='%s';"%(accession_number))

def check_if_incomplete(accession_number):
    cursor.execute("SELECT * FROM balance WHERE accession_number='%s';"%(accession_number))
    balance_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM income WHERE accession_number='%s';"%(accession_number))
    income_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM cash_flow WHERE accession_number='%s';"%(accession_number))
    cash_flow_entry = cursor.fetchall()

    return (len(balance_entry) == 0 or len(income_entry) == 0 or len(cash_flow_entry) == 0)

#run for just 2009 range(2009, 2010)
years = list(range(2020, 2021))

#total count to keep track of how many files we've gone through
total_count = 0

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
            master_file_name = file['name'].strip('.gz') if '.gz' in file['name'] else file['name']
            fileURL = makeURL(baseURL, [year, item['name'], file['name']])

            # Grab the Master IDX file URL
            if 'master' in fileURL:
                cursor.execute("SELECT status FROM master_idx WHERE master_file='%s';"%(master_file_name))
                status = cursor.fetchone()
                cursor.execute("SELECT * FROM master_idx WHERE master_file='%s';"%(master_file_name))
                idx_list = cursor.fetchall()
                if len(idx_list) == 0:
                    sql_statement = "INSERT INTO master_idx (master_file, status) VALUES ('%s', '%s');"%(master_file_name, 'PENDING')
                    cursor.execute(sql_statement)
                    print(sql_statement)
                    print(f"Parsing {master_file_name} now")
                elif status[0] == 'COMPLETED':
                    print(f"Completed parsing of {master_file_name}")
                    continue
                elif status[0] == 'ERROR' or status[0] == 'PENDING':
                    print(f"Parsing {master_file_name} now")

                # Request that new content, this will NOT be a JSON STRUCTURE
                if '.gz' in fileURL:
                    fileContent = urllib.request.urlopen(fileURL)
                    compressedFile = BytesIO(fileContent.read())
                    decompressedFile = gzip.GzipFile(fileobj=compressedFile)
                    with open(master_file_name, 'wb') as f:
                        f.write(decompressedFile.read())

                    with open(master_file_name, 'rb') as f:
                        with open('master_file_text.txt', 'wb') as w:
                            w.write(f.read())

                    os.remove(master_file_name)

                    with open('master_file_text.txt', 'rb') as f:
                        byteData = f.readlines()
                else:
                    fileContent = requests.get(fileURL).content

                    with open('master_file_text.txt', 'wb') as f:
                        f.write(fileContent)

                    # We now have a byte stream of data
                    with open('master_file_text.txt','rb') as f:
                        byteData = f.readlines()

                os.remove('master_file_text.txt')
                headers = unidecode.unidecode(restore_windows_1252_characters(unicodedata.normalize('NFKD', byteData[5].decode('utf-8'))))
                headers = headers.strip().split('|')
                headers = [header.lower().replace(' ','') for header in headers]
                fileData = byteData[7:]

                # We need to split the data into sections so we can get each row value
                for index in fileData:

                    # Clean it up.
                    try:
                        index = unidecode.unidecode(restore_windows_1252_characters(unicodedata.normalize('NFKD', index.decode('utf-8'))))
                    except UnicodeDecodeError:
                        continue
                    index_split = index.strip().split('|')
                    if index_split[2] != '10-K' and index_split[2] != '10-Q':
                        continue
                    cursor.execute("SELECT * FROM company WHERE cik=%s;"%(int(index_split[0])))
                    if len(cursor.fetchall()) < 1:
                        continue

                    # Create the URL
                    index_split_modify = index_split[4].split('/')
                    index_split[4] = ''
                    index_split_accession = ''.join(index_split_modify[3].strip('.txt').split('-'))
                    for x in index_split_modify[:-1]:
                        index_split[4] = index_split[4] + '/' + x
                    index_url = "https://www.sec.gov/Archives" + index_split[4] + '/' + index_split_accession + '/' + index_split_modify[-1].strip('.txt') + '-index.htm'
                    index_split[4] = index_split[4] + '/' + index_split_accession + '/' + index_split_modify[-1]
                    index_split[4] = "https://www.sec.gov/Archives" + index_split[4]

                    # Create a list of dictionaries with the file header as keys and each row as values
                    filing_dict = dict(zip(headers, index_split))
                    text_filing = filing_dict['filename']
                    response = requests.get(text_filing)
                    soup = BeautifulSoup(response.content, 'lxml')

                    if len(soup.find_all('filename')) == 0: # Skip if the filename tag is not in the text filing summary
                        continue
                    if '.htm' not in soup.find_all("filename")[0].get_text(): # Skip if .htm not in filename (meaning it's a .txt file)
                        continue
                    accession_number = text_filing.split('/')[-1].strip('.txt') # Extract accession number (after last '/') & remove '.txt'
                    accession_exist = cursor.execute("SELECT * FROM scrape WHERE accession_number = '%s';"%(accession_number))

                    if len(cursor.fetchall()) > 0: # Skip if filing with that accession number is already inserted
                        print(f'Already inserted -- Link: {filing_dict["filename"]}, Date: {filing_dict["datefiled"]}')
                        continue

                    url_list = text_filing.split('/')
                    url_xml = ''
                    for part in url_list[:-1]:
                        url_xml = url_xml + '' + part + '/'
                    url_xml = url_xml + 'FilingSummary.xml' # Get Filing Summary XML tree

                    find_year = BeautifulSoup(requests.get(index_url).content, 'lxml')
                    report_period = find_year.find('div', text='Period of Report')
                    actual_year = filing_dict["datefiled"][0:4] if report_period is None else report_period.find_next_sibling('div').text[0:4]
                    period_of_report = report_period.find_next_sibling('div').text

                    tree = ET.fromstring(requests.get(url_xml).text)
                    if 'NoSuchKey' in tree[0].text and index_split[2] == '10-K': # Insert HTM ONLY IF it's a 10-K and has NoSuchKey in the first child node of the root
                        sql_statement = "INSERT INTO scrape (cik_id, filing_type, year, file_name, accession_number, inter_or_htm, status) VALUES(%s, '%s', %s, '%s', '%s', '%s', '%s');"%(int(filing_dict["cik"]), filing_dict["formtype"], actual_year, filing_dict["filename"], accession_number, 'HTM', 'PENDING')
                        cursor.execute(sql_statement)
                        total_count+=1
                        print(sql_statement)
                        print('Total Count: ' +str(total_count))
                    elif 'NoSuchKey' not in tree[0].text and (index_split[2] == '10-K' or index_split[2] == '10-Q'): # Insert Interactive Data ONLY IF it's a 10-K OR 10-Q and DOES NOT have NoSuchKey (it actually has a valid XML tree structure)
                        sql_statement = "INSERT INTO scrape (cik_id, filing_type, year, file_name, accession_number, inter_or_htm, status) VALUES(%s, '%s', %s, '%s', '%s', '%s', '%s');"%(int(filing_dict["cik"]), filing_dict["formtype"], actual_year, filing_dict["filename"], accession_number, 'Inter', 'PENDING')
                        cursor.execute(sql_statement)
                        total_count+=1
                        print(sql_statement)
                        print('Total Count: ' +str(total_count))

                        """ try: # Try to run interParse; any error thrown will result in an ERROR status code for the current master IDX file & any deletions from the scrape, balance, income, cash flow, and non statement tables to prevent errors when parsing again
                            interParse(index_url, accession_number, index_split[2])

                            if check_if_incomplete(accession_number):
                                cursor.execute("UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s';"%(accession_number))
                                delete_from_tables(accession_number)
                            else:
                                cursor.execute("UPDATE scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession_number))
                        except:
                            cursor.execute("UPDATE master_idx SET status='ERROR' WHERE master_file='%s'"%(master_file_name))
                            delete_from_tables(accession_number)
                            cursor.execute("UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s'"%(accession_number)) """

                sql_statement = "UPDATE master_idx SET status='COMPLETED' WHERE master_file='%s'"%(master_file_name)
                cursor.execute(sql_statement)
                print(sql_statement)
                print(f"Completed parsing of {master_file_name}")
