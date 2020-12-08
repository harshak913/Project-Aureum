import re
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import psycopg2
from operator import itemgetter
import os
from itertools import groupby

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
        #print(n_value)
        #convert to in millions through this
        if unit == 'As Displayed':
            n_value = float(n_value)/1000000
        elif unit == 'In Thousands':
            n_value = float(n_value)/1000
        #if it was negative add the bracket to signfigy negative
        if negative > 0:
            n_value = '-' + str(n_value)
        value = n_value
    return value

#accession_number = '0001193125-11-047795' #NEG ONE EXAMPLE uses -
accession_number = "0001018724-16-000172" #NEG ONE EXAMPLE uses ()
tables = ['balance','cash_flow','income']
numbers_finished = 0
for table in tables:
    #grab the balance, cash or income table and match it with the accession_number
    scrape_query = "select * from %s where accession_number = '%s';"%(table, accession_number)
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
        #print(months_ended)
        #make sure that it's not a member
        if '[' not in member:
            if 'MEMBER' not in member.upper():
                if 'SERIES' not in member.upper():
                    if 'FACILITY' not in member.upper():
                        if '[' not in eng_name:
                            #unit conversion from thousand and as displayed to millions
                            if unit == 'As Displayed' or unit == 'In Thousands':
                                print(acc_name, unit, value)
                                #Check if share or not. "Per" and "Share" or "Stock". If Not Proceed
                                if 'Per' not in acc_name:
                                    value = cleaning(value)
                                elif 'Per' and 'Share' not in acc_name:
                                    value = cleaning(value)
                                elif 'Per' and 'Stock' not in acc_name:
                                    value = cleaning(value)
                                #IF PER EXISTS BUT IT'S PERIOD
                                if ',' in str(value) and 'Per' in acc_name:
                                    if 'Period' in acc_name:
                                        value = cleaning(value)
                                dict = {}
                                dict['member'] = member
                                dict['header'] = header
                                dict['eng_name'] = eng_name
                                dict['acc_name'] = acc_name
                                dict['value'] = value
                                dict['unit'] = 'In Millions'
                                dict['year'] = year
                                dict['report_period'] = report_period
                                dict['statement'] = table
                                dict['filing_type'] = filing_type
                                dict['accession_number'] = accession_number
                                if re.sub('[\W_]+', '', str(dict['value'])).isdigit():
                                    if months_ended == '':
                                        total_dict.append(dict)
                                    elif '12' in months_ended:
                                        total_dict.append(dict)
                            #if in millions do this
                            else:
                                value = cleaning(value)
                                dict = {}
                                dict['member'] = member
                                dict['header'] = header
                                dict['eng_name'] = eng_name
                                dict['acc_name'] = acc_name
                                dict['value'] = value
                                dict['unit'] = 'In Millions'
                                dict['year'] = year
                                dict['report_period'] = report_period
                                dict['statement'] = table
                                dict['filing_type'] = filing_type
                                dict['accession_number'] = accession_number
                                #print(dict)
                                if re.sub('[\W_]+', '', str(dict['value'])).isdigit():
                                    if months_ended == '':
                                        total_dict.append(dict)
                                    elif '12' in months_ended:
                                        total_dict.append(dict)
    #print(total_dict)
    #All values from this statement have been properly compiled. Time to standardize
    scrape_query_2 = "select * from standard_dict where statement = '%s';"%(table)
    cursor.execute(scrape_query_2)
    johns = cursor.fetchall()
    final_standard = []
    avoids = ['Net Income', 'Operating Income', 'Total Revenue', 'Net Change in Cash', 'Gross Profit', 'Total Equity', 'Total Liabilities And Equity', 'Total Current Assets']
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
        avoid_check = [item for item in avoids if item == avoid_pass['standard_name']]
        if count > 1:
            #see if this is an item we cannot compound. if not means the list is empty. if this is empty means there are no matches
            if not avoid_check:
                print('THIS IS COMPOUNDABLE')
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

    line_items = 0
    for item in the_end:
        line_items+=1
        #print(item)
        if table == 'balance':
            statement_insert = 'standard_balance'
        elif table == 'cash_flow':
            statement_insert = 'standard_cash'
        elif table == 'income':
            statement_insert = 'standard_income'
        #print(item['standard_name'], item['acc_name'], item['value'], item['current_year'])
        sql_statement = "INSERT INTO %s (accession_number, header, standard_name, eng_name, acc_name, value, unit, year, statement, report_period, filing_type) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"%(statement_insert, accession_number, item['header'], item['standard_name'], item['eng_name'], item['acc_name'], item['value'], item['unit'], item['year'], item['statement'], item['report_period'], item['filing_type'])
        print(sql_statement)
        #cursor.execute(sql_statement)
    print('FINAL LINE ITEMS FOR THIS STATEMENT IS: ' +str(line_items))
"""
    k = itemgetter('standard_name','current_year')
    i = groupby(sorted(final_standard, key=k), key=k)
    for key, final_standard in i:
        #print(key)
        count = 0
        copy = []
        for item in final_standard:
            count+=1
            copy.append(item)
        #print(count)
        if count > 1:
            for item in copy:
                #print(item)

            for query in querys:
                print(standard_name, acc_name)
                print(query)
                #check if this item is allowed to be compounded or not
                avoid_check = [item for item in avoids if item == query['standard_name']]
                #if can be compounded
                if not avoid_check:
                    checks = [item for item in final_standard if item['standard_name'] == query['standard_name'] and item['current_year'] == query['current_year'] and item['acc_name'] != query['acc_name']]
                    #print(checks)
                    if checks:
                        for item in final_standard:
                            if item['standard_name'] == query['standard_name'] and item['current_year'] == query['current_year'] and item['acc_name'] != query['acc_name']:
                                print('THERE IS ALREADY AN EXISTING ONE')
                                #print(checks)
                                #print('THIS IS THE CURRENT ITEM')
                                #print(query)
                                #print('L169')
                                #add the names together.
                                if query['acc_name'] not in item['acc_name']:
                                    item['acc_name'] = str(item['acc_name']) +", " + str(query['acc_name'])
                                if query['eng_name'] not in item['eng_name']:
                                    item['eng_name'] = str(item['eng_name'])+' + '+str(query['eng_name'])
                                #COMPILE THE NUMBERS NOW
                                item['cumulative'] = True
                                item['value'] = float(item['value']) + float(query['value'])

                    else:
                        print('THIS DOES NOT EXIST AND WE MUST ADD IT AS THE FIRST OCCURENCE')
                        #print(query)
                        final_standard.append(query)
                        #print(final_standard)

                else:
                    print('THIS IS NOT COMPOUNDABLE')
                    checks = [item for item in final_standard if item['standard_name'] == query['standard_name'] and item['current_year'] == query['current_year'] and item['acc_name'] != query['acc_name']]
                    #print(checks)
                    if not checks:
                        final_standard.append(query)


    #for d in final_standard:
        #print(d)
    #print('NOW TALLYING FINAL BUNCH')
    for item in final_standard:
        print(item)

    seen = set()
    new_l = []
    for d in final_standard:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)



    j = 0
    for item in new_l:
        j+=1
        #print(item)
        if table == 'balance':
            statement_insert = 'standard_balance'
        elif table == 'cash_flow':
            statement_insert = 'standard_cash'
        elif table == 'income':
            statement_insert = 'standard_income'
        #print(item['standard_name'], item['acc_name'], item['value'], item['current_year'])
        sql_statement = "INSERT INTO %s (accession_number, header, standard_name, eng_name, acc_name, value, unit, year, statement, report_period, filing_type) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"%(statement_insert, accession_number, item['header'], item['standard_name'], item['eng_name'], item['acc_name'], item['value'], item['unit'], item['year'], item['statement'], item['report_period'], item['filing_type'])
        print(sql_statement)
        #cursor.execute(sql_statement)
    print('Total Line Items: '+str(j))
    print('ITEMS PARSED TO THIS POINT: '+str(numbers_finished))


INSERT INTO standard_income (accession_number, header, standard_name, eng_name, acc_name, value, unit, year, statement, report_period, filing_type) VALUES('0001018724-16-000172', 'Operating expenses:', 'Other Non-Operating Inc. (Exp.)', 'Interest expense(-459)', 'InterestExpense', '-459', 'In Millions', '2015-12-31', 'income', '2015-12-31', '10-K');

INSERT INTO standard_income (accession_number, header, standard_name, eng_name, acc_name, value, unit, year, statement, report_period, filing_type) VALUES('0001018724-16-000172', 'Operating expenses:', 'Other Non-Operating Inc. (Exp.)', 'Other income (expense), net(-256) + Interest expense(-459)', 'OtherNonoperatingIncomeExpense, InterestExpense', '-715.0', 'In Millions', '2015-12-31', 'income', '2015-12-31', '10-K');
"""
