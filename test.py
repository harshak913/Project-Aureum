import requests
#from HTMLFinal import HTMLParse
from bs4 import BeautifulSoup
import psycopg2
import os
import wikipedia as wiki
#from Inter_Table import interParse

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

""" connection2 = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="DB^oo^ec@^h@ckth!$0913")
connection2.autocommit = True
cursor2 = connection2.cursor() """

def delete_from_tables(accession_number):
    cursor.execute("DELETE FROM balance WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM income WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM cash_flow WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM non_statement WHERE accession_number='%s'"%(accession_number))

def check_if_incomplete(accession_number):
    cursor.execute("SELECT * FROM balance WHERE accession_number='%s';"%(accession_number))
    balance_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM income WHERE accession_number='%s';"%(accession_number))
    income_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM cash_flow WHERE accession_number='%s';"%(accession_number))
    cash_flow_entry = cursor.fetchall()

    return (len(balance_entry) == 0 or len(income_entry) == 0 or len(cash_flow_entry) == 0)

#Reset all inters in scrape to pending and delete them from 3 statements
"""cursor.execute("SELECT accession_number FROM scrape WHERE inter_or_htm='Inter';")
for test in cursor.fetchall():
    delete_from_tables(test[0])
    cursor.execute("UPDATE scrape SET status='PENDING' WHERE accession_number='%s';"%(test[0]))"""

# Run scrape for HTML insertion
""" cursor.execute("SELECT * FROM scrape WHERE year=2009 AND inter_or_htm='HTM' AND status='PENDING';")
results = cursor.fetchall()
for count, result in enumerate(results):
    if count >= 10:
        break
    print(result)
    index_page = result[3].strip('.txt') + "-index.htm"
    accession_number = result[4]
    response = requests.get(index_page)
    soup = BeautifulSoup(response.content, 'lxml')
    period_of_report = soup.find('div', text='Period of Report').find_next_sibling('div').text

    try:
        print(f"PARSING {result[3]} NOW")
        HTMLParse(result[3], '10k', accession_number, result[1], period_of_report)

        if check_if_incomplete(accession_number):
            sql_statement = "UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s';"%(accession_number)
            cursor.execute(sql_statement)
            print(sql_statement + "\n")
            delete_from_tables(accession_number)
        else:
            sql_statement = "UPDATE scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession_number)
            cursor.execute(sql_statement)
            print(sql_statement + "\n")
    except:
        if os.path.exists('10k-balance_sheet.csv'):
            os.remove('10k-balance_sheet.csv')
        if os.path.exists('10k-income_statement.csv'):
            os.remove('10k-income_statement.csv')
        if os.path.exists('10k-cash_flows.csv'):
            os.remove('10k-cash_flows.csv')
        delete_from_tables(accession_number)
        sql_statement = "UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s'"%(accession_number)
        cursor.execute(sql_statement)
        print(sql_statement + "\n") """

# Delete table rows
""" cursor.execute("SELECT * FROM scrape WHERE inter_or_htm='Inter';")
results = cursor.fetchall()
for result in results:
    accession_number = result[4]
    delete_from_tables(accession_number)
    cursor.execute("UPDATE scrape SET status='PENDING' WHERE accession_number='%s';"%(accession_number))
    print("UPDATE scrape SET status='PENDING' WHERE accession_number='%s';"%(accession_number)) """

# SIC classification name update
""" soup = BeautifulSoup(requests.get('https://www.sec.gov/info/edgar/siccodes.htm').content, 'lxml')
tr_list = soup.find('table', attrs={"class": "sic"}).find('tbody').find_all('tr')
sic_dict = {}
for tr in tr_list[1:]:
    td_list = tr.find_all('td')
    sic_dict[int(td_list[0].get_text())] = td_list[2].get_text()
cursor.execute("SELECT cik, classification FROM company;")
sic_num = cursor.fetchall()
for tup in sic_num:
    cursor.execute("UPDATE company SET classification_name='%s' WHERE cik=%s;"%(sic_dict[tup[1]].replace("'", "''"), tup[0])) """

# Prettify HTML files
""" prettified = BeautifulSoup(requests.get('https://www.sec.gov/Archives/edgar/data/1051470/000144530511000263/0001445305-11-000263.txt').content, 'lxml').prettify()
with open("testHTML.htm", "w", encoding='utf-8') as file:
    file.write(prettified) """

#Fix scrape table status error
""" cursor.execute("SELECT accession_number FROM scrape WHERE inter_or_htm='HTM';")
htm_accessions = cursor.fetchall()
for accession in htm_accessions:
    if not check_if_incomplete(accession[0]):
        cursor.execute("UPDATE scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession[0])) """

#Check if all COMPLETED HTMs are actually completed
""" cursor.execute("SELECT accession_number FROM scrape WHERE year=2010 AND inter_or_htm='HTM';")
for tup in cursor.fetchall():
    if check_if_incomplete(tup[0]):
        print(tup[0]) """

# Run InterParse
""" years = list(range(2010, 2021))

for year in years:
    cursor.execute("SELECT * FROM scrape WHERE year=%s AND inter_or_htm='Inter' AND status='PENDING';"%(year))
    results = cursor.fetchall()
    for result in results:
        print(result)
        index_page = result[3].strip('.txt') + "-index.htm"
        accession_number = result[4]
        response = requests.get(index_page)
        soup = BeautifulSoup(response.content, 'lxml')
        period_of_report = soup.find('div', text='Period of Report').find_next_sibling('div').text

        try: # Try to run interParse; any error thrown will result in an ERROR status code for the current master IDX file & any deletions from the scrape, balance, income, cash flow, and non statement tables to prevent errors when parsing again
            print(f"PARSING {result[3]} NOW")
            interParse(index_page, accession_number, result[1])

            if check_if_incomplete(accession_number):
                print("UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s';"%(accession_number))
                cursor.execute("UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s';"%(accession_number))
                delete_from_tables(accession_number)
            else:
                print("UPDATE scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession_number))
                cursor.execute("UPDATE scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession_number))
        except:
            delete_from_tables(accession_number)
            print("UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s'"%(accession_number))
            cursor.execute("UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s'"%(accession_number)) """

#Copy standard_dict data to Heroku cloud DB
""" cursor2.execute("SELECT * FROM standard_dict;")
results = cursor2.fetchall()
for result in results:
    cursor.execute("INSERT INTO standard_dict (standard_name, acc_name, statement) VALUES ('%s', '%s', '%s');"%(result[0], result[1], result[2])) """

# Update company names with direct data from SEC
""" cursor.execute("SELECT cik, name FROM company ORDER BY name ASC;")
cikList = cursor.fetchall()

for c in cikList:
    if c[1] in ('Business', 'U.S.', 'World', 'Technology', 'Entertainment', 'Science', 'Health'):
        continue
    cik = str(c[0])
    for i in range(10-len(cik)):
        cik = '0' + cik
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=%s&owner=exclude'%(cik)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    print(url)
    updated_name_list = soup.find('div', attrs={"class" : "companyInfo"}).get_text()
    name = ''
    for index in range(len(updated_name_list)):
        if 'CIK' in updated_name_list[index]:
            break
        if index == 0:
            name = updated_name_list[index]
        else:
            name = name + ' ' + updated_name_list[index]
    print(name) """

# Fix name capitalization
""" cursor.execute("SELECT name FROM company ORDER BY ticker ASC;")
companies = cursor.fetchall()
for company in companies:
    name = company[0].split('/')[0].split('\\')[0]

    if name in ('Business', 'U.S.', 'World', 'Technology', 'Entertainment', 'Science', 'Health'):
        continue

    nameList = name.split()
    for i in range(len(nameList)):
        name = nameList[i][0] + nameList[i][1:].lower() if i == 0 else (name + ' ' + nameList[i][0] + nameList[i][1:].lower())
    print(name) """

# Update company info
""" cursor.execute("SELECT ticker, name FROM company ORDER BY ticker ASC;")
tickers = cursor.fetchall()
for t in tickers:
    ticker = yf.Ticker(t[0])
    name = t[1].split('/')[0]

    if name in ('Business', 'U.S.', 'World', 'Technology', 'Entertainment', 'Science', 'Health'):
        continue

    print(name)
    info = ticker.info
    print(info)

    if len(info) == 1:
        cursor.execute("UPDATE company SET hq='', website='', full_time_employees=0, logo_url='' WHERE ticker='%s';"%(t[0]))
    
    if 'country' in info:
        if 'United States' == info['country']:
            hq = f"{info['address1']}\n{info['city']}, {info['state']}\n{info['country']}\n{info['zip']}".replace("'", "''") if ('address1' in info and 'state' in info and 'city' in info and 'zip' in info) else ''
        else:
            hq = f"{info['city']}, {info['country']}".replace("'", "''") if 'city' in info else ''
    else:
        hq = ''
    
    website = info['website'] if 'website' in info else ''
    full_time_employees = info['fullTimeEmployees'] if 'fullTimeEmployees' in info else 0 #Change to int value
    logo_url = info['logo_url'] if 'logo_url' != '' else ''
    print(f"{website}\n{hq}\n{full_time_employees}\n{logo_url}\n")
    cursor.execute("UPDATE company SET hq='%s', website='%s', full_time_employees=%s, logo_url='%s' WHERE ticker='%s';"%(hq, website, full_time_employees, logo_url, t[0]))
 """
# Get description from wiki
""" try:
        description = wiki.summary(name)
        if name.split()[0] not in description:
            description = info['longBusinessSummary']
    except:
        description = info['longBusinessSummary'] """