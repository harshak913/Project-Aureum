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


def interParse(filing_index, accession_number, filing_type):
    #once you get filing index url find the report period
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
    balance_sheet_variations = ['NET ASSET', 'POSITION', 'BALANCE SHEET', 'CONDITION', 'FINANCIAL STATEMENT']

    income_statement_variations = ['EARNING', 'OPERATION', 'INCOME', 'LOSS']

    cash_flows_variations = ['CASH FLOW']

    non_signs = ['PARENTHETICAL', 'SUPPLEMENTARY', 'TAXES']

    #print(all_dict)

    income_found = False
    cash_found = False
    balance_found = False
    already_taken = []


    children = []
    html = open("%s.htm"%latter).read()
    soup = BeautifulSoup(html, features="lxml")
    JS_Portion = soup.find("script", attrs={"type" : 'text/javascript' ,"language" : 'javascript'}).string
    #^ JS_Portion is for later on, don't worry about it
    dicts = []
    for element in soup.find_all('li'):
        if financialStatementsFound != True:
            if element.get('class') is not None:
                if str(element.get('class')[0]).strip() == 'accordion':
                    if element.get('id') is not None:
                        print(str(element.text).strip().upper())
                        child = element.find('a')
                        #got the child element for the statement and now get the link and name
                        numbers = {}
                        number = str(child['href'])
                        number = number.replace('javascript:loadReport(', '')
                        number = number.replace(');', '')
                        numbers['number'] = str(number)
                        numbers['name'] = str(child.text).strip()
                        dicts.append(numbers)
                        statement = str(element.text).strip().upper()
                        if not any(x in statement.upper() for x in non_signs):
                            if any(x in statement.upper() for x in cash_flows_variations) and cash_found == False and statement not in already_taken:
                                true_cash = str(statement)
                                cash_found = True
                                already_taken.append(str(statement))
                                print(statement)
                                print('CASH FLOW FOUND')
                            elif any(x in statement.upper() for x in balance_sheet_variations) and balance_found == False and statement not in already_taken:
                                true_balance = str(statement)
                                balance_found = True
                                already_taken.append(str(statement))
                                print(statement)
                                print('BALANCE FOUND')
                            elif any(x in statement.upper() for x in income_statement_variations) and income_found == False and statement not in already_taken:
                                true_income = str(statement)
                                income_found = True
                                already_taken.append(str(statement))
                                print(statement)
                                print('INCOME FOUND')

                        if cash_found == True and balance_found == True and income_found == True:
                            financialStatementsFound = True

        else:
            break
    '''
        if str(element.text).strip() == 'Notes to Financial Statements' and element.find_next_sibling('ul') is not None:
            john = element.find_next_sibling('ul')
            dict_2 = []
            marks = john.findChildren('a')
        Refer to link bellow to see a case where 'Notes to Financial Statements' comes up twice
        #https://www.sec.gov/cgi-bin/viewer?action=view&cik=49826&accession_number=0000049826-16-000151&xbrl_type=v#

    print('Getting the name and number for the reports')
    #GET THE NAME AND NUMBER FOR THE FINANCIAL REPORTS
    '''

    '''
    for child in children:
        numbers = {}
        number = str(child['href'])
        number = number.replace('javascript:loadReport(', '')
        number = number.replace(');', '')
        numbers['number'] = str(number)
        numbers['name'] = str(child.text).strip()
        dicts.append(numbers)
    '''

    reports = []
    #ASSEMBLE THE LIST OF ALL THE POSSIBLE LINKS TO THE ARCHIVE
    for line in JS_Portion.split('\n'):
        if 'reports[' and '] = "/Archives/edgar/data/' in line:
            reports.append(line.strip())

    print('matching correct report number with the correct dict')
    #match correct report number with the correct dict
    for report in reports:
        print(report)
        comp = report.split('] = "/Archives/edgar/data/', 1)[0]
        comp = comp.replace('reports[', '')
        comp = str(eval(comp))
        for item in dicts:
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
    dummy = dicts.copy()
    dicts = []
    for item in dummy:
        if item['number'].isdigit():
            dicts.append(item)
    #TIME TO PARSE THE ACTUAL FINANCIAL STATEMENTS
    print('TIME TO PARSE THE ACTUAL FINANCIAL STATEMENTS')
    for item in dicts:
        #HTM PARSE SECTION HERE
        if 'htm' in item['link']:
            #CREATE THE DOCUMENT AND BEAUTIFULSOUP PARSE IT
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
            member_header = ''
            header = ''
            months_ended = []
            extension = 1
            #this for loop gets the proper span lengths for the months ended
            for one in ones:
                l = one.text.strip()
                if re.search('months ended', l, re.IGNORECASE) is not None:
                    months = {}
                    if one.has_attr('colspan'):
                        col = int(one.get('colspan'))
                        months['start_span'] = int(extension)
                        extension += col
                        months['end_span'] = int(extension) - 1
                    months['months_ended'] = l.strip()
                    months_ended.append(months)

            #everything from these years must be ###<= x =<###
            for item in months_ended:
                print(item)

            #TIME TO MATCH THE DATES TO THE MONTHS ENDED
            id = 1
            for one in ones:
                l = one.text.strip()
                match = re.match(r'.*([1-3][0-9]{3})', l)
                if match is not None:
                    dates = {}
                    if one.has_attr('colspan'):
                        col = int(one.get('colspan'))
                        dates['start_span'] = int(id)
                        id += (col)
                        dates['end_span'] = int(id) - 1
                        dates['date'] = match.group(0)
                        check_id = dates['end_span']
                        for item in months_ended:
                            if item.get('start_span') is not None:
                                start_span = int(item.get('start_span'))
                                end_span = int(item.get('end_span'))
                                if check_id >= start_span and check_id <= end_span:
                                    dates['months_ended'] = item.get('months_ended')
                        all_dates.append(dates)
                    else:
                        date = {}
                        date['id'] = int(id)
                        date['date'] = match.group(0)
                        for item in months_ended:
                            if item.get('start_span') is not None:
                                start_span = int(item.get('start_span'))
                                end_span = int(item.get('end_span'))
                                if id >= start_span and id <= end_span:
                                    date['months_ended'] = item.get('months_ended')
                        all_dates.append(date)
                        id+=1

            for date in all_dates:
                print(date)

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
                            if element.find('a') is not None and element.find('a').get('onclick') is not None:
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
                                    if any('start_span' in d for d in all_dates):
                                        for item in all_dates:
                                            #split it further to see if there is id. 0001067701-14-000004 is a good example of when there is id & span mix
                                            if 'id' in item:
                                                if item['id'] == id:
                                                    date = str(item['date'])
                                                    if item.get('months_ended') is not None:
                                                        months_ended = str(item['months_ended'])
                                                        id+=1
                                                        break
                                                    else:
                                                        months_ended = ''
                                                        id+=1
                                                        break
                                            #if not an id do the usual span method
                                            else:
                                                date = str(item['date'])
                                                start_span = int(item.get('start_span'))
                                                end_span = int(item.get('end_span'))
                                                if id >= start_span and id <= end_span:
                                                    if item.get('months_ended') is not None:
                                                        months_ended = str(item['months_ended'])
                                                        id+=1
                                                        break
                                                    else:
                                                        months_ended = ''
                                                        id+=1
                                                        break
                                    elif any('id' in d for d in all_dates):
                                        for item in all_dates:
                                            if item['id'] == id:
                                                date = str(item['date'])
                                                if item.get('months_ended') is not None:
                                                    months_ended = str(item['months_ended'])
                                                    id+=1
                                                    break
                                                else:
                                                    months_ended = ''
                                                    id+=1
                                                    break

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
                                        print(dict['eng_name'], dict['value'], dict['date'], dict['months_ended'])
                                        all_dict.append(dict)
            #for item in all_dict:
            #    print(item['eng_name'], item['value'], item['date'], item['months_ended'])
            os.remove(filename)



        #XML PARSE SECTION HERE
        elif 'xml' in item['link']:
            doc_name = str(item.get('name'))
            print('NOW PARSING '+doc_name+ ' (A XML DOC)')
            filename = "/Users/octavian/Desktop/HTM/%s.xml"%(doc_name)
            #filename = "/Users/Harsh/OneDrive - The University of Texas at Dallas/Documents/Project A/HTM/%s.xml"%(doc_name)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            report_access = 'https://www.sec.gov%s'%str(item.get('link'))
            page = requests.get(report_access)
            soup = BeautifulSoup(page.content, features="lxml")
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
                    match = re.match(r'.*([1-3][0-9]{3})', l)
                    if match is not None:
                        dates['date'] = match.group(0)
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
                            print(dict['eng_name'], dict['value'], dict['date'], dict['months_ended'])
                            all_dict.append(dict)
            os.remove(filename)

    #store data in POSTGRESQL
    balance_sheet_variations = ['NET ASSET', 'POSITION', 'BALANCE SHEET', 'CONDITION', 'FINANCIAL STATEMENT']

    income_statement_variations = ['EARNING', 'OPERATION', 'INCOME', 'LOSS']

    cash_flows_variations = ['CASH FLOW']

    non_signs = ['PARENTHETICAL', 'SUPPLEMENTARY', 'TAXES']


    income_found = False
    cash_found = False
    balance_found = False
    already_taken = []

    for item in all_dict:
        statement = str(item.get('statement')).replace("'", '').strip()
        if not any(x in statement.upper() for x in non_signs):
            if any(x in statement.upper() for x in cash_flows_variations) and cash_found == False and statement not in already_taken:
                true_cash = str(statement)
                cash_found = True
                already_taken.append(str(statement))
                print(statement)
                print('CASH FLOW FOUND')
            elif any(x in statement.upper() for x in balance_sheet_variations) and balance_found == False and statement not in already_taken:
                true_balance = str(statement)
                balance_found = True
                already_taken.append(str(statement))
                print(statement)
                print('BALANCE FOUND')
            elif any(x in statement.upper() for x in income_statement_variations) and income_found == False and statement not in already_taken:
                true_income = str(statement)
                income_found = True
                already_taken.append(str(statement))
                print(statement)
                print('INCOME FOUND')

    for item in all_dict:
        #get the variables for inserting from the item dict
        member = str(item.get('member')).replace("'", '').strip()
        header = str(item.get('header')).replace("'", '').strip()
        acc_name = str(item.get('acc_name')).strip()
        value = str(item.get('value')).replace('$', '').strip()
        year = item.get('date')
        try:
            if 'Sept' in year:
                year_list = year.split(' ')
                year = year_list[0][0:3] + '. ' + year_list[1] + ' ' + year_list[2]
            year = datetime.strptime(str(year), '%b. %d, %Y')
            year = year.strftime('%Y-%m-%d')
        except ValueError:
            try:
                year = datetime.strptime(str(year), '%b %d, %Y')
                year = year.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    year = datetime.strptime(str(year), '%B. %d, %Y')
                    year = year.strftime('%Y-%m-%d')
                except:
                    try:
                        year = datetime.strptime(str(year), '%B %d, %Y')
                        year = year.strftime('%Y-%m-%d')
                    except:
                        continue
        except:
            continue
        eng_name = str(item.get('eng_name')).replace("'", '').strip()
        statement = str(item.get('statement')).replace("'", '').strip()
        months_ended = str(item.get('months_ended')).replace("'", '').strip()
        unit = str(item.get('unit')).replace("'", '').strip()

#.replace("'", '')
        #run the code for unit and context first
        if not any(x in statement.upper() for x in non_signs):
            if any(x in statement.upper() for x in cash_flows_variations) and statement == true_cash:
                print('CASH FLOW')
                statement_insert = 'cash_flow'
            elif any(x in statement.upper() for x in income_statement_variations) and statement == true_income:
                print('INCOME STATEMENT')
                statement_insert = 'income'
            elif any(x in statement.upper() for x in balance_sheet_variations) and statement == true_balance:
                print('BALANCE SHEET')
                statement_insert = 'balance'
            else:
                print('NONSTATEMENT')
                statement_insert = 'non_statement'
        else:
            statement_insert = 'non_statement'

        sql_statement = "INSERT INTO %s (accession_number, member, header, eng_name, acc_name, value, unit, year, statement, report_period, filing_type, months_ended) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"%(statement_insert, accession_number, member, header, eng_name, acc_name, value, unit, year, statement, report_period, filing_type, months_ended)
        try:
            print(sql_statement)
            cursor.execute(sql_statement)
        except:
            continue
#print('PROGRAM IS FINISHED')

#print(all_dict)
