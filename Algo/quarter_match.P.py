import re
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import psycopg2
import os
from itertools import groupby
from operator import itemgetter
import operator

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

def cleaning(value):
    negative = 0
    #check if there is a negative indicator
    if '(' in value:
        negative+=1
    if '-' in value:
        negative+=1
    removelist = "."
    #print(value)
    n_value = re.sub(r'[^\w'+removelist+']', '',value)
    #get rid of both negatives and positives
    if re.sub('[\W_]+', '', n_value).isdigit():
        #if it was negative add the bracket to signfigy negative
        if negative > 0:
            n_value = '-' + str(n_value)
        value = n_value
    return value

def quarter_mod(q_current, q_prior):
    #insert q_current and q_past
    modif_q = []
    #q_base = q2_cash.copy()+q1_cash.copy()
    q_base = q_current.copy() + q_prior.copy()
    #GRAB HIGHEST QUARTER AND ORDER
    seq = [x['order'] for x in q_base.copy()]
    highest_q = max(seq)
    quarter_q = next(item for item in q_base.copy() if item["order"] == highest_q)['quarter']
    print(highest_q, quarter_q)
    print('HIGHEST Q IS: '+str(highest_q))
    #SORT THE ITEMS BY STANDARD NAMES
    k = itemgetter('standard_name')
    i = groupby(sorted(q_base, key=k), key=k)
    for key, q_base in i:
        print(key)
        list_c = []
        count = 0
        for item in q_base:
            count+=1
            list_c.append(item)
            check = item.copy()
        print(count)
        if count == 2:
            #sharelist determines whether or not we sub or keep current one
            share_list = ['Basic EPS', 'Diluted EPS', 'Weighted Avg. Diluted Shares Out.','Weighted Avg. Basic Shares Out.']
            share_check = [share for share in share_list if share == check['standard_name']]
            if not share_check:
                seq = [x['order'] for x in list_c]
                highest = max(seq)
                lowest = min(seq)
                high_val = next(item for item in list_c if item["order"] == highest).copy()
                low_val = next(item for item in list_c if item["order"] == lowest).copy()
                print(high_val['quarter'],high_val['standard_name'], high_val['value'], high_val['accession_number'])
                print(low_val['quarter'],low_val['standard_name'], low_val['value'], low_val['accession_number'])
                new_val_q = float(high_val['value']) - float(low_val['value'])
                #create eng_version with the names and vals concocetnated
                high_val['eng_name'] = str(high_val['eng_name']) + " - " + str(low_val['eng_name'])
                high_val['value'] = round(new_val_q, 2)
                print('MODIFIED WITH SUBTRACTION')
                modif_q.append(high_val)
                print(high_val['quarter'],high_val['standard_name'], high_val['value'], high_val['accession_number'], high_val['current_year'])
            else:
                seq = [x['order'] for x in list_c]
                highest = max(seq)
                lowest = min(seq)
                high_val = next(item for item in list_c if item["order"] == highest).copy()
                low_val = next(item for item in list_c if item["order"] == lowest).copy()
                print(high_val['quarter'],high_val['standard_name'], high_val['value'], high_val['accession_number'])
                print(low_val['quarter'],low_val['standard_name'], low_val['value'], low_val['accession_number'])
                #now tell us what has happened
                print('CANNOT SUBTRACT SO WE TAKE THE HIGHER ONE')
                modif_q.append(high_val)
                print(high_val['quarter'],high_val['standard_name'], high_val['value'], high_val['accession_number'], high_val['current_year'])

        elif count == 1:
            for item in list_c.copy():
                if item['order'] == highest_q:
                    #KEEP THIS THE SAME AND JUST APPEND IT
                    print('Higher Quarter SOLO')
                    modif_q.append(item)
                    print(item['quarter'],item['standard_name'], item ['value'], item['accession_number'])
                else:
                    #MULTIPLE BY -1 TO IMITATE - AND THEN MODIFY THE QUARTER TO THE CURRENT HIGHEST Q
                    print('Lower Quarter SOLO')
                    print(item['quarter'],item['standard_name'], item ['value'], item['accession_number'], item['current_year'])
                    item['value'] = round(float(item['value']) * -1.0, 2)
                    item['quarter'] = quarter_q
                    print('MODIFIED NOW TO BE NEGATIVE')
                    modif_q.append(item)
                    print(item['quarter'],item['standard_name'], item ['value'], item['accession_number'], item['current_year'])
    return(modif_q)


#START OF MAIN PROGRAM BODY
#Grab company
scrape_query = "select * from company;"
cursor.execute(scrape_query)
entries = cursor.fetchall()
#Grab CIK number and then connect it to scrape to get 10-Q
total_parse = 0
for entry in entries:
    total_parse+=1
    cik = str(entry[0])
    ticker = str(entry[1])
    print(cik)
    current_year = 2009
    #years completed =
    scrape_query = "select * from scrape where cik_id = '%s' and year = '%s';"%(cik, current_year)
    print(scrape_query)
    cursor.execute(scrape_query)
    filing_entries = cursor.fetchall()
    print(filing_entries)
    q1 = False
    q2 = False
    q3 = False
    q4 = False
    for item in filing_entries:
        if item[7] == 'Q1' and item[6] == 'COMPLETED':
            q1 = True
            print('Q1 TRUE')
        if item[7] == 'Q2' and item[6] == 'COMPLETED':
            q2 = True
            print('Q2 TRUE')
        if item[7] == 'Q3' and item[6] == 'COMPLETED':
            q3 = True
            print('Q3 TRUE')
        if item[1] == '10-K' and item[6] == 'COMPLETED':
            q4 = True
            print('Q4 TRUE')

    if q1 == True and q2 == True and q3 == True and q4 == True:
        print('THIS YEAR HAS ALL 3Qs ACCOUNTED FOR')
        quarter_list = []
        q1_cash = []
        q1_income = []
        q1_balance = []
        q2_cash = []
        q2_income = []
        q2_balance = []
        q3_cash = []
        q3_income = []
        q3_balance = []
        q4_cash = []
        q4_income = []
        q4_balance = []
        for item in filing_entries:
            if item[7] == 'Q1':
                indiv = {}
                indiv['quarter'] = 'Q1'
                indiv['accession_number'] = item[4]
                indiv['order'] = 1
                quarter_list.append(indiv)
            if item[7] == 'Q2':
                indiv = {}
                indiv['quarter'] = 'Q2'
                indiv['accession_number'] = item[4]
                indiv['months_ended'] = '6 Months Ended'
                indiv['order'] = 2
                quarter_list.append(indiv)
            if item[7] == 'Q3':
                indiv = {}
                indiv['quarter'] = 'Q3'
                indiv['accession_number'] = item[4]
                indiv['months_ended'] = '9 Months Ended'
                indiv['order'] = 3
                quarter_list.append(indiv)
            if item[1] == '10-K':
                indiv = {}
                indiv['quarter'] = 'Q4'
                indiv['accession_number'] = item[4]
                indiv['order'] = 4
                quarter_list.append(indiv)

        def get_order(item):
            return item.get('order')

        quarter_list.sort(key=get_order)

        print(quarter_list)

        for q in quarter_list:
            tables = ['income','cash_flow', 'balance']
            quarter = str(q['quarter'])
            order = float(q['order'])
            print('NOW CURRENTLY RUNNING: '+quarter)
            for table in tables:
                accession_number = q['accession_number']
                if 'months_ended' in q and table != 'balance':
                    print('THERE ARE MONTHS ENDED STATEMENT IS '+table)
                    print(q['months_ended'])
                    months_ended = q['months_ended']
                    scrape_query = "select * from %s where accession_number = '%s' and months_ended  = '%s' and date_part('year', year) = '%s';"%(table, accession_number, months_ended, current_year)
                else:
                    print('TABLE IS EQUAL TO BALANCE')
                    scrape_query = "select * from %s where accession_number = '%s' and date_part('year', year) = '%s';"%(table, accession_number, current_year)
                #scrape_query = "select * from %s where accession_number = '%s';"%(table, accession_number)
                print(scrape_query)
                cursor.execute(scrape_query)
                smiths = cursor.fetchall()
                #time to go through the table
                total_dict = []
                for smith in smiths:
                    access = str(smith[0])
                    member = str(smith[1])
                    header = str(smith[2])
                    eng_name = str(smith[3])
                    acc_name = str(smith[4])
                    value = str(smith[5])
                    if ' ' in value:
                        value = str(smith[5]).split(' ', 1)[0]
                        value = value.strip('\n').strip()
                    if value == '':
                        value = str('0')
                    unit = str(smith[6])
                    year = str(smith[7])
                    report_period = str(smith[9])
                    filing_type = str(smith[10])
                    months_ended = str(smith[11])
                    #make sure that it's not a member
                    if '[' not in member:
                        if 'MEMBER' not in member.upper():
                            if 'SERIES' not in member.upper():
                                if 'FACILITY' not in member.upper():
                                    if '[' not in eng_name:
                                        value = cleaning(value)
                                        dict = {}
                                        dict['member'] = member
                                        dict['header'] = header
                                        dict['eng_name'] = eng_name
                                        dict['acc_name'] = acc_name
                                        dict['value'] = value
                                        dict['unit'] = unit
                                        dict['year'] = year
                                        dict['report_period'] = report_period
                                        dict['statement'] = table
                                        dict['filing_type'] = filing_type
                                        dict['accession_number'] = accession_number
                                        dict['quarter'] = quarter
                                        dict['order'] = order
                                        total_dict.append(dict)
                #print(total_dict)
                #All values from this statement have been properly compiled. Time to standardize
                scrape_query_2 = "select * from standard_dict where statement = '%s';"%(table)
                cursor.execute(scrape_query_2)
                johns = cursor.fetchall()
                final_standard = []
                #avoids are items that can't be compounded
                avoids = ['Net Income',
                'Operating Income',
                'Net Change in Cash',
                'Gross Profit',
                'Total Equity',
                'Total Liabilities And Equity',
                'Total Current Assets',
                'Total Revenue'
                'Total Assets',
                'Total Current Liabilities',
                'Total Liabilities',
                'Total Common Equity',
                'Total Shares Out.'
                'Total Equity',
                'Total Liabilities And Equity',
                'Operating Exp., Total',
                'Net Income to Company',
                'Cash from Ops.',
                'Cash from Investing',
                'Cash from Financing',
                'Basic EPS',
                'Weighted Avg. Basic Shares Out.',
                'Diluted EPS',
                'Earnings from Cont. Ops.',
                'Earnings of Discontinued Ops.',
                'Weighted Avg. Diluted Shares Out.',
                'Net Change in Cash']

                highest_val = ['Revenue',
                'Cost Of Goods Sold']

                for john in johns:
                    standard_name = john[0]
                    acc_name = john[1]
                    #print(standard_name, acc_name)
                    #querys are the total values that are equal to an acc_name item in total
                    querys = [item for item in total_dict if item['acc_name'] == acc_name]
                    current_querys = []
                    if querys:
                        #give current status to the querys
                        for query in querys:
                            query1 = query.copy()
                            current_year = str(query1['year']).split('-',1)[0]
                            query1['current_year'] = current_year
                            query1['standard_name'] = standard_name
                            query_value = str(query1['value'])
                            query1['eng_name'] = str(query['eng_name'])+'('+query_value+')'
                            final_standard.append(query1)

                #remove duplicates
                seen = set()
                new_l = []
                for d in final_standard:
                    t = tuple(d.items())
                    if t not in seen:
                        seen.add(t)
                        new_l.append(d)

                #CLEAN THE UNITS FOR THOSE WITH AS DISPLAYED OR THOUSANDS
                for new in new_l:
                    unit = new['unit']
                    if unit == 'In Thousands' or unit == 'As Displayed':
                        share_list = ['Basic EPS', 'Diluted EPS']
                        share_check = [item for item in share_list if item == new['standard_name']]
                        if not share_check:
                            print('PRIOR VALUE: ')
                            print(new['value'])
                            if unit == 'As Displayed':
                                n_value = float(new['value'])/1000000
                            elif unit == 'In Thousands':
                                n_value = float(new['value'])/1000
                            print('NEW VALUE: ')
                            new['value'] = n_value
                            print(new['value'])
                            new['unit'] = 'In Millions'
                        else:
                            new['unit'] = 'In Millions'

                the_end = []
                k = itemgetter('standard_name','current_year')
                i = groupby(sorted(new_l, key=k), key=k)
                for key, new_l in i:
                    print(key)
                    count = 0
                    copy = []
                    for item in new_l:
                        count+=1
                        copy.append(item)
                        avoid_pass = item.copy()
                    print(count)
                    #avoid check is to make sure that they are compoundable
                    avoid_check = [item for item in avoids if item == avoid_pass['standard_name']]
                    #highest check sees if we need to take the highest value for this item
                    highest_check = [item for item in highest_val if item == avoid_pass['standard_name']]
                    if count > 1:
                        #see if this is an item we cannot compound. if not means the list is empty. if this is empty means there are no matches
                        if not avoid_check:
                            print('THIS IS COMPOUNDABLE')
                            #if highest checks then take the largest value and then move on
                            if highest_check:
                                maxItem = max(copy, key=lambda x:x['value'])
                                highest = maxItem.copy()
                                the_end.append(highest)
                            else:
                                first = 0
                                for item in copy:
                                    if first == 0:
                                        template = item.copy()
                                        first+=1
                                    else:
                                        template['acc_name'] = str(template['acc_name']) +", " + str(item['acc_name'])
                                        template['eng_name'] = str(template['eng_name'])+' + '+str(item['eng_name'])
                                        #COMPILE THE NUMBERS NOW
                                        template['value'] = float(template['value']) + float(item['value'])
                                        template['cumulative'] = True
                                the_end.append(template)
                        #else means that there is a match with the avoid. This means no compounding
                        else:
                            print('THIS IS NOT COMPOUNDABLE')
                            first = 0
                            for item in copy:
                                if first == 0:
                                    the_end.append(item)
                                    first+=1
                    else:
                        for item in copy:
                            the_end.append(item)

                if quarter == 'Q1' and table == 'cash_flow':
                    print('Q1 CASH FLOW')
                    for item in the_end:
                        q1_cash.append(item)
                elif quarter == 'Q1' and table == 'income':
                    print('Q1 INCOME')
                    for item in the_end:
                        q1_income.append(item)
                elif quarter == 'Q1' and table == 'balance':
                    print('Q1 BALANCE')
                    for item in the_end:
                        q1_balance.append(item)
                elif quarter == 'Q2' and table == 'cash_flow':
                    print('Q2 CASH FLOW')
                    for item in the_end:
                        q2_cash.append(item)
                elif quarter == 'Q2' and table == 'income':
                    print('Q2 INCOME')
                    for item in the_end:
                        q2_income.append(item)
                elif quarter == 'Q2' and table == 'balance':
                    print('Q2 BALANCE')
                    for item in the_end:
                        q2_balance.append(item)
                elif quarter == 'Q3' and table == 'cash_flow':
                    print('Q3 CASH FLOW')
                    for item in the_end:
                        q3_cash.append(item)
                elif quarter == 'Q3' and table == 'income':
                    print('Q3 INCOME')
                    for item in the_end:
                        q3_income.append(item)
                elif quarter == 'Q3' and table == 'balance':
                    print('Q3 BALANCE')
                    for item in the_end:
                        q3_balance.append(item)
                elif quarter == 'Q4' and table == 'cash_flow':
                    print('Q4 CASH FLOW')
                    for item in the_end:
                        q4_cash.append(item)
                elif quarter == 'Q4' and table == 'income':
                    print('Q4 INCOME')
                    for item in the_end:
                        q4_income.append(item)
                elif quarter == 'Q4' and table == 'balance':
                    print('Q4 BALANCE')
                    for item in the_end:
                        q4_balance.append(item)



        finale = []

        #INSERT BALANCE
        for item in q1_balance:
            finale.append(item)
        for item in q2_balance:
            finale.append(item)
        for item in q3_balance:
            finale.append(item)
        for item in q4_balance:
            finale.append(item)


        #INSERT CASH
        q2_cash_f = []
        q3_cash_f = []
        q4_cash_f = []
        #start of actual processing
        q1_cash_f = q1_cash
        if q2_cash and q1_cash:
            q2_cash_f = quarter_mod(q2_cash, q1_cash)
        if q3_cash and q2_cash:
            q3_cash_f = quarter_mod(q3_cash, q2_cash)
        if q4_cash and q3_cash:
            q4_cash_f = quarter_mod(q4_cash, q3_cash)
        #if all quarters are present besides Q1 then append
        if q2_cash_f and q3_cash_f and q4_cash_f:
            for item in q1_cash_f:
                finale.append(item)
            for item in q2_cash_f:
                finale.append(item)
            for item in q3_cash_f:
                finale.append(item)
            for item in q4_cash_f:
                finale.append(item)

        #INSERT INCOME
        q2_income_f = []
        q3_income_f = []
        q4_income_f = []
        #start of actual
        q1_income_f = q1_income
        if q2_income and q1_income:
            q2_income_f = quarter_mod(q2_income, q1_income)
        if q3_income and q2_income:
            q3_income_f = quarter_mod(q3_income, q2_income)
        if q4_income and q3_income:
            q4_income_f = quarter_mod(q4_income, q3_income)
        #if all are present then append all items to finale
        if q2_income_f and q3_income_f and q4_income_f:
            for item in q1_income_f:
                finale.append(item)
            for item in q2_income_f:
                finale.append(item)
            for item in q3_income_f:
                finale.append(item)
            for item in q4_income_f:
                finale.append(item)

#895421

        line_items = 0
        for item in finale:
            line_items+=1
            #print(item)
            if item['statement'] == 'balance':
                statement_insert = 'standard_balance'
            elif item['statement'] == 'cash_flow':
                statement_insert = 'standard_cash'
            elif item['statement'] == 'income':
                statement_insert = 'standard_income'
            print(item['standard_name'], item['acc_name'], item['value'], item['quarter'], item['current_year'], item['statement'])
            #sql_statement = "INSERT INTO %s (accession_number, header, standard_name, eng_name, acc_name, value, unit, year, statement, report_period, filing_type, quarter) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"%(statement_insert, item['accession_number'], item['header'], item['standard_name'], item['eng_name'], item['acc_name'], item['value'], item['unit'], item['year'], item['statement'], item['report_period'], item['filing_type'], item['quarter'])
            #print(sql_statement)
            #cursor.execute(sql_statement)
        print('FINAL LINE ITEMS FOR THIS STATEMENT IS: ' +str(line_items))
        print('TOTAL COMPANIES PARSED TO THIS POINT: ' + str(total_parse))


'''
    q1 = False
    q2 = False
    q3 = False
    all_q = False
    for item in filing_entries:
        if item[7] = 'Q1':
            q1 = True
        if item[7] = 'Q2':
            q2 = True
        if item[7] = 'Q3':
            q3 = True
    if q1 = True and q2 = True and q3 = True:
        print('THIS YEAR HAS ALL 3Qs ACCOUNTED FOR')
    else:
        print('THIS YEAR DOES NOT HAVE ALL 3Qs ACCOUNTED FOR')

cik = '1048695' # in Thousands 2015
#cik = '1306830' # as displayed 2013
current_year = '2015'
scrape_query = "select * from scrape where cik_id = '%s' and year = '%s';"%(cik,current_year) #use 2010 and 2011
cursor.execute(scrape_query)
filing_entries = cursor.fetchall()
'''
