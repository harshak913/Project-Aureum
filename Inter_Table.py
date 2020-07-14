import re
import urllib.request
from bs4 import BeautifulSoup, NavigableString
import os
import xml.etree.ElementTree as ET
import requests
import psycopg2
from datetime import datetime
from dateutil.relativedelta import relativedelta
#begin code
#input the txt filing
#filing_summary = "https://www.sec.gov/Archives/edgar/data/65172/000155837018002967/0001558370-18-002967.txt"
#filing_summary = "https://www.sec.gov/Archives/edgar/data/1067983/000119312510043450/0001193125-10-043450.txt"
#filing_summary = "https://www.sec.gov/Archives/edgar/data/27093/000117152016001006/0001171520-16-001006.txt"
#filing_summary = "https://www.sec.gov/Archives/edgar/data/1638290/000155837016008267/0001558370-16-008267.txt"
#filing_summary = "https://www.sec.gov/Archives/edgar/data/32689/000104746912001313/0001047469-12-001313.txt"
#filing_summary = "https://www.sec.gov/Archives/edgar/data/789019/000119312510090116/0001193125-10-090116.txt"

#filing_summary = "https://www.sec.gov/Archives/edgar/data/1067983/000115752310002982/0001157523-10-002982.txt" #Q1
#filing_summary = "https://www.sec.gov/Archives/edgar/data/1067983/000115752310004882/0001157523-10-004882.txt" #Q2
#filing_summary = "https://www.sec.gov/Archives/edgar/data/1067983/000115752310006675/0001157523-10-006675.txt" #Q3

#filing_summary = "https://www.sec.gov/Archives/edgar/data/1067983/000095012319009995/0000950123-19-009995.txt" #Q3


#Database Connection
psycopg2.connect(host="ec2-34-233-226-84.compute-1.amazonaws.com", dbname="d77knu57t1q9j9", user="jsnmfiqtcggjyu", password="368e05099543272efb167e9fa3173338be43c1e787666ed2478f51ef050707b9")
connection.autocommit = True
cursor = connection.cursor()


def interParse(filing_index, accession_number, filing_type):
    #once you get filing index url, get the xml_url and xml file name
    response = requests.get(filing_index)
    soup = BeautifulSoup(response.content, 'lxml')
    report_period = soup.find('div', text='Period of Report')
    report_period = report_period.find_next_sibling('div').text
    data_files = soup.find('table', attrs={'summary':'Data Files'})
    if data_files.find('td', text='EX-101.INS') is not None:
        file_type = data_files.find('td', text='EX-101.INS')
    elif data_files.find('td', text='XML') is not None:
        file_type = data_files.find('td', text='XML')
    if '.xml' in file_type.find_previous('td').text:
        xml = file_type.find_previous('td').text
    else:
        xml = file_type.find_next('td').text
    xml_url = ''
    for i in range(len(url_list)-1):
        xml_url = xml_url + '' + url_list[i] + '/'
    xml_url = xml_url + '' + xml

    ticker = xml.split('-')[0]

    #index portion
    index = filing_index
    result = index.split('/')
    result = list(filter(None, result))
    cik = int(result.index('data'))+1
    cik = str(result[cik]) #CIK IS THE CIK NUMBER

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

    '''
    #now download the xml page and save it for reading, and save the file path for later
    xml_filepath = "/Users/octavian/Desktop/XML/%s/%s"%(latter,xml)
    xml_filepath = str(xml_filepath)
    os.makedirs(os.path.dirname(xml_filepath), exist_ok=True)
    page = urllib.request.urlopen(xml_url).read()
    soup = BeautifulSoup(page, features="lxml")
    pretty = soup.prettify()
    with open(xml_filepath, "w") as f:
        f.write(pretty)
    '''

    #CHECK THE INTERACTIVE PAGE AND GET THE NUMBER LINKS FOR NOTES AND FINANCIAL STATEMENTS
    html = open("%s.htm"%latter).read()
    soup = BeautifulSoup(html, features="lxml")
    JS_Portion = soup.find("script", attrs={"type" : 'text/javascript' ,"language" : 'javascript'}).text
    for element in soup.find_all('a'):
        if str(element.text).strip() == 'Financial Statements':
            relevant = element.find_next_sibling('ul')
            dicts = []
            children = relevant.findChildren('a')
        if str(element.text).strip() == 'Notes to Financial Statements':
            john = element.find_next_sibling('ul')
            dict_2 = []
            marks = john.findChildren('a')

    #GET THE NAME AND NUMBER FOR THE FINANCIAL REPORTS
    for child in children:
        numbers = {}
        number = str(child['href'])
        number = number.replace('javascript:loadReport(', '')
        number = number.replace(');', '')
        numbers['number'] = str(number)
        numbers['name'] = str(child.text).strip()
        dicts.append(numbers)

    #GET THE NAME AND NUMBER FOR THE NOTES TO FINANCIAL REPORTS
    '''
    for mark in marks:
        numbers = {}
        number = str(mark['href'])
        number = number.replace('javascript:loadReport(', '')
        number = number.replace(');', '')
        numbers['number'] = str(number)
        numbers['name'] = str(mark.text).strip()
        dict_2.append(numbers)
    '''

    reports = []
    #ASSEMBLE THE LIST OF ALL THE POSSIBLE LINKS TO THE ARCHIVE
    for line in JS_Portion.split('\n'):
        if 'reports[' and '] = "/Archives/edgar/data/' in line:
            reports.append(line.strip())

    #match correct report number with the correct dict
    for report in reports:
        comp = report.split('] = "/Archives/edgar/data/', 1)[0]
        comp = comp.replace('reports[', '')
        comp = str(eval(comp))
        for item in dicts:
            if item["number"] == comp:
                link = report.split('= "', 1)[1]
                item['link'] = link.replace('";', '')
        for item in dict_2:
            if item["number"] == comp:
                link = report.split('= "', 1)[1]
                item['link'] = link.replace('";', '')

    all_dict = []

    os.remove("%s.htm"%latter)

    #NOW SAVE THE NOTES OF TO THE FINANCIAL STATEMENTS
    '''
    for item in dict_2:
        if 'htm' in item['link']:
            doc_name = str(item.get('name'))
            filename = "/Users/octavian/Desktop/HTM/%s/notes/%s.htm"%(latter, doc_name.replace('/', ' '))
            os.makedirs(os.path.dirname(filename), exist_ok=True)
    #        os.makedirs('/Users/octavian/Desktop/XML/%s'%latter)
            report_access = 'https://www.sec.gov%s'%str(item.get('link'))
            page = urllib.request.urlopen(report_access).read()
            soup = BeautifulSoup(page, features="lxml")
            pretty = soup.prettify()
            with open(filename, "w") as f:
                f.write(pretty)
        elif 'xml' in item['link']:
            doc_name = str(item.get('name'))
            filename = "/Users/octavian/Desktop/HTM/%s/notes/%s.xml"%(latter, doc_name.replace('/', ' '))
            os.makedirs(os.path.dirname(filename), exist_ok=True)
    #        os.makedirs('/Users/octavian/Desktop/XML/%s'%latter)
            report_access = 'https://www.sec.gov%s'%str(item.get('link'))
            page = urllib.request.urlopen(report_access).read()
            soup = BeautifulSoup(page, features="lxml")
            pretty = soup.prettify()
            with open(filename, "w") as f:
                f.write(pretty)
    '''

    #TIME TO PARSE THE ACTUAL FINANCIAL STATEMENTS
    for item in dicts:
        if 'htm' in item['link']:
            #CREATE THE DOCUMENT AND BEAUTIFULSOUP PARSE IT
            doc_name = str(item.get('name'))
            filename = "/Users/octavian/Desktop/HTM/%s.htm"%(doc_name)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            report_access = 'https://www.sec.gov%s'%str(item.get('link'))
            page = urllib.request.urlopen(report_access).read()
            soup = BeautifulSoup(page, features="lxml")
            pretty = soup.prettify()
            with open(filename, "w") as f:
                f.write(pretty)
            htm = open(filename).read()
            soup = BeautifulSoup(htm , features="lxml")

            #GET THE STATEMENT'S NAME
            statement_name = str(soup.find('th').text).strip()
            statement_name = statement_name.split()
            statement_name = ' '.join(statement_name)

            #CHECK IF THE UNIT IS GIVEN
            if 'IN MILLIONS' in statement_name.upper():
                unit = 'In Millions'
            elif 'IN THOUSANDS' in statement_name.upper():
                unit = 'In Thousands'
            else:
                unit = 'As Displayed'

            #NOW GET THE DATES
            all_dates = []
            ones = soup.find_all('th')
            id = 1
            member_header = ''
            header = ''
            months_ended = []
            extension = 0
            col_id = 1
            for one in ones:
                l = one.text.strip()
                if re.search('months ended', l, re.IGNORECASE) is not None:
                    months = {}
                    if one.has_attr('colspan') and col_id==1:
                        col = int(one.get('colspan'))
                        months['start_span'] = extension
                        months['end_span'] = col
                        extension += col
                        col_id+=1
                    elif one.has_attr('colspan') and col_id != 1:
                        col = int(one.get('colspan'))
                        months['start_span'] = extension
                        extension += col
                        months['end_span'] = extension
                    months['months_ended'] = l.strip()
                    months_ended.append(months)
            for one in ones:
                l = one.text.strip()
                if re.match(r'.*([1-3][0-9]{3})', l) is not None:
                    date = {}
                    date['id'] = id
                    date['date'] = l.upper().split('USD', 1)[0].strip()
                    for item in months_ended:
                        if item.get('start_span') is not None:
                            start_span = int(item.get('start_span'))
                            end_span = int(item.get('end_span'))
                            if id > start_span and id <= end_span:
                                date['months_ended'] = item.get('months_ended')
                    all_dates.append(date)
                    id+=1

            #CHECK IF THIS STATEMENT IS PARSABLE BECAUSE WE DON'T WANT TO GET THE SHAREHOLDER'S EQUITY

            go = 0
            for item in all_dates:
                if 'date' in item:
                    go +=1
            #IF GO IS NOT 0 THEN IT CONTAINS DATES AND IS PARSABLE
            if go != 0:
                #FIND ALL THE ROWS IN THE TABLE
                for element in soup.find('table').find_all('tr'):
                    if element.find_all('td') is not None:
                        children = element.find_all('td')
                        #CHECK THAT THE ROW IS IN FACT A LINE ITEM OR AT LEAST A HEADER
                        if element.find('td') is not None and element.find('td').text.strip() != '':
                            #CHECK IF THIS ITEM HAS A US-GAAP TAG TO MATCH IT
                            if element.find('a') is not None:
                                acc_name = element.find('a').get('onclick').replace("top.Show.showAR( this, 'defref_", '')
                                acc_name = acc_name.split("', window );", 1)[0]
                                acc_name = acc_name.split("_", 1)[1]
                            #SAVE THE ENGLISH NAME
                            eng_name = element.find('td').text.strip()

                            #CHECK IF THIS IS A HEADER, AND THUS ONLY CONTAINS AN ENGLISH NAME
                            header_check = 0
                            for child in children:
                                if child.text.strip() != '':
                                    header_check += 1

                            #CHECK IF NEXT ROW IS A HEADER. IF THIS IS FULFILLED THAT MEANS THE CURRENT ROW IS A MEMBER
                            next_check = 0
                            if element.find_next_sibling('tr') is not None:
                                nexts = element.find_next_sibling('tr').find_all('td')
                                for next in nexts:
                                    if next.text.strip() != '':
                                        next_check +=1

                            #RUN THE GAUNTLET TO SEE IF IT IS MEMBER, HEADER OF JUST A REGULAR LINE ITEM
                            if header_check == 1 and 'MEMBER' in eng_name.upper() and '[' in eng_name.upper():
                                member_header = eng_name
                            elif header_check == 1 and next_check == 1:
                                member_header = eng_name
                            elif header_check == 1 and next_check != 1:
                                header = eng_name
                            elif header_check > 1:
                                id = 1
                                #SET ID TO MATCH THE NUMBERS TO THE PROPER YEAR. THE 1: SKIPS OVER THE ENGLISH NAME SO WE CAN ASSIGN THE NUMBERS
                                for child in children[1:]:
                                    for item in all_dates:
                                        if item['id'] == id:
                                            date = item['date']
                                            if item.get('months_ended') is not None:
                                                months_ended = item['months_ended']
                                            else:
                                                months_ended = ''
                                    if child.find('sup') is None and child.find('span') is not None:
                                        dict = {}
                                        dict['member'] = member_header.strip()
                                        dict['header'] = header.strip()
                                        dict['eng_name'] = eng_name.strip()
                                        dict['value'] = child.text.strip()
                                        dict['date'] = ' '.join(date.split())
                                        dict['months_ended'] = months_ended
                                        dict['statement'] = statement_name.strip()
                                        dict['acc_name'] = acc_name.strip()
                                        dict['unit'] = unit.strip()
                                        #print(dict)
                                        all_dict.append(dict)
                                        id+=1
            os.remove(filename)


        elif 'xml' in item['link']:
            doc_name = str(item.get('name'))
            filename = "/Users/octavian/Desktop/HTM/%s.xml"%(doc_name)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            report_access = 'https://www.sec.gov%s'%str(item.get('link'))
            page = urllib.request.urlopen(report_access).read()
            soup = BeautifulSoup(page, features="lxml")
            pretty = soup.prettify()
            with open(filename, "w") as f:
                f.write(pretty)
            # parse the tables and match the values
            xml = open(filename).read()
            soup = BeautifulSoup(xml , features="lxml")
            statement_name = str(soup.find('reportname').text).strip()
            #clean up the statement name
            statement_name = statement_name.split()
            statement_name = ' '.join(statement_name)
            if 'IN MILLIONS' in statement_name.upper():
                unit = 'In Millions'
            elif 'IN THOUSANDS' in statement_name.upper():
                unit = 'In Thousands'
            else:
                unit = 'As Displayed'
            all_dates = []
            for element in soup.find_all('column'):
                dates = {}
                labels = element.find_all('label')
                for label in labels:
                    l = label.get('label')
                    if re.match(r'.*([1-3][0-9]{3})', l) is not None:
                        dates['date'] = l.upper().split('USD', 1)[0].strip()
                    if re.search('months ended', l, re.IGNORECASE) is not None:
                        dates['months_ended'] = l.strip()
                dates['id'] = element.find('id').text.strip()
                all_dates.append(dates)
            member_header = ''
            header = ''
            go = 0
            for item in all_dates:
                if 'date' in item:
                    go +=1
            if go != 0:
                for element in soup.find_all('row'):
                    this_row = []
                    #clean up english name
                    eng_name = ' '.join(str(element.find('label').text).strip().split())
                    acc_name = str(element.find('elementname').text).strip()
                    if acc_name != '':
                        acc_name = str(element.find('elementname').text).strip().split('_', 1)[1]
                    children = element.find_all('cell')
                    header_check = 0
                    for child in children:
                        if child.find('numericamount').text.strip() != '0':
                            header_check +=1

                    next_check = 0
                    if element.find_next_sibling('row') is not None:
                        nexts = element.find_next_sibling('row').find_all('cell')
                        for next in nexts:
                            if next.find('numericamount').text.strip() != '0':
                                next_check +=1

                    if header_check == 0 and 'MEMBER' in str(eng_name).upper() and '[' in str(eng_name).upper():
                        member_header = eng_name
                    elif header_check == 0 and next_check == 0:
                        member_header = eng_name
                    elif header_check == 0 and 'MEMBER' not in str(eng_name).upper() and next_check != 0:
                        header = eng_name
                    else:
                        for child in children:
                            dict = {}
                            value = child.find('numericamount').text
                            id = child.find('id').text.strip()
                            for item in all_dates:
                                if id == item['id']:
                                    current_date = item['date']
                                    if item.get('months_ended') is not None:
                                        months_ended = item['months_ended']
                                    else:
                                        months_ended = ''
                            dict['member'] = member_header.strip()
                            dict['header'] = header.strip()
                            dict['eng_name'] = eng_name.strip()
                            dict['value'] = value.strip()
                            dict['date'] = current_date.strip()
                            dict['months_ended'] = months_ended
                            dict['statement'] = statement_name.strip()
                            dict['acc_name'] = acc_name.strip()
                            dict['unit'] = unit.strip()
                            #print(dict)
                            all_dict.append(dict)
            os.remove(filename)


    #store data in POSTGRESQL
    balance_sheet_variations = ['NET ASSET', 'FINANCIAL POSITION', 'BALANCE SHEET']

    income_statement_variations = ['EARNING', 'OPERATION', 'INCOME']

    cash_flows_variations = ['CASH FLOW']

    non_signs = ['PARENTHETICAL', 'COMPREHENSIVE','SUPPLEMENTARY', 'EQUITY']


    for item in all_dict:
        #get the variables for inserting from the item dict
        member = str(item.get('member'))
        header = str(item.get('header'))
        acc_name = str(item.get('acc_name'))
        value = str(item.get('value'))
        try:
            year = datetime.strptime(str(item.get('date')), '%b. %d, %Y')
            year = year.strftime('%Y-%m-%d')
        except:
            continue
        eng_name = str(item.get('eng_name'))
        statement = str(item.get('statement'))
        months_ended = str(item.get('months_ended'))
        unit = str(item.get('unit'))


        #run the code for unit and context first
        if not any(x in statement.upper() for x in non_signs):
            if any(x in statement.upper() for x in cash_flows_variations):
                print('CASH FLOW')
                statement_insert = 'cash_flow'
            elif any(x in statement.upper() for x in income_statement_variations):
                print('INCOME STATEMENT')
                statement_insert = 'income'
            elif any(x in statement.upper() for x in balance_sheet_variations):
                print('BALANCE SHEET')
                statement_insert = 'balance'
            else:
                print('NONSTATEMENT')
                statement_insert = 'non_statement'
        else:
            statement_insert = 'non_statement'

    else:
        statement_insert = 'non_statement'
    sql_statement = "INSERT INTO database.%s (accession_number, member, header, eng_name, acc_name, value, unit, year, statement, report_period, filing_type, months_ended) VALUES(%s, '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"%(statement_insert, accession_number, member, header, eng_name, acc_name, value, unit, year, statement, report_period, filing_type, months_ended)
    print(statement_sql)
    cursor.execute(statement_sql)
#print('PROGRAM IS FINISHED')

#print(all_dict)
