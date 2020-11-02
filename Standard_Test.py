import re
import pandas as pd
import psycopg2
import os

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()
'''
scrape_query = "select * from scrape where filing_type = '10-K' and inter_or_htm = 'Inter' and year = '2016';"
cursor.execute(scrape_query)
entries = cursor.fetchall()
for entry in entries:
    accession_number = str(entry[4])
    tables = ['standard_balance','standard_cash','standard_income']
    for table in tables:
        sql_statement = "delete from %s where accession_number = '%s'"%(table, accession_number)
        print(sql_statement)
        cursor.execute(sql_statement)


'''
#table = 'cash_flow'
table = 'balance'
#table = 'income'
#accession_number = "0000827054-19-000143" #as Displayed
#accession_number = "0001707925-18-000004" #NEEDS TO BE TESTED
accession_number = '0000818479-18-000014'#Tested BEFORE 50 rows select * from balance where accession_number = '0000818479-18-000014';
#accession_number = "0000054480-16-000143" #in millions

avoids = ['Net Income', 'Operating Income', 'Total Revenue', 'Net Change in Cash', 'Gross Profit', 'Total Equity', 'Total Liabilities And Equity', 'Total Current Assets']

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
                                negative = 0
                                #check if there is a negative indicator
                                if '(' in value:
                                    negative+=1
                                if '-' in value:
                                    negative+=1
                                removelist = "."
                                #print(value)
                                n_value = re.sub(r'[^\w'+removelist+']', '',value)
                                if n_value.replace('.','').isdigit():
                                    #print(n_value)
                                    #convert to in millions through this
                                    if unit == 'As Displayed':
                                        n_value = float(n_value)/1000000
                                    elif unit == 'In Thousands':
                                        n_value = float(n_value)/1000
                                    #if it was negative add the bracket to signfigy negative
                                    if negative > 0:
                                        n_value = '(' + str(n_value) + ')'
                                    value = n_value
                            elif 'Per' and 'Share' not in acc_name:
                                negative = 0
                                #check if there is a negative indicator
                                if '(' in value:
                                    negative+=1
                                if '-' in value:
                                    negative+=1
                                removelist = "."
                                #print(value)
                                n_value = re.sub(r'[^\w'+removelist+']', '',value)
                                if n_value.replace('.','').isdigit():
                                    #print(n_value)
                                    #convert to in millions through this
                                    if unit == 'As Displayed':
                                        n_value = float(n_value)/1000000
                                    elif unit == 'In Thousands':
                                        n_value = float(n_value)/1000
                                    #if it was negative add the bracket to signfigy negative
                                    if negative > 0:
                                        n_value = '(' + str(n_value) + ')'
                                    value = n_value
                            elif 'Per' and 'Stock' not in acc_name:
                                negative = 0
                                #check if there is a negative indicator
                                if '(' in value:
                                    negative+=1
                                if '-' in value:
                                    negative+=1
                                removelist = "."
                                #print(value)
                                n_value = re.sub(r'[^\w'+removelist+']', '',value)
                                if n_value.replace('.','').isdigit():
                                    #print(n_value)
                                    #convert to in millions through this
                                    if unit == 'As Displayed':
                                        n_value = float(n_value)/1000000
                                    elif unit == 'In Thousands':
                                        n_value = float(n_value)/1000
                                    #if it was negative add the bracket to signfigy negative
                                    if negative > 0:
                                        n_value = '(' + str(n_value) + ')'
                                    value = n_value
                            #IF PER EXISTS BUT IT'S PERIOD
                            if ',' in str(value) and 'Per' in acc_name:
                                if 'Period' in acc_name:
                                    negative = 0
                                    #check if there is a negative indicator
                                    if '(' in value:
                                        negative+=1
                                    if '-' in value:
                                        negative+=1
                                    removelist = "."
                                    #print(value)
                                    n_value = re.sub(r'[^\w'+removelist+']', '',value)
                                    if n_value.replace('.','').isdigit():
                                        #print(n_value)
                                        #convert to in millions through this
                                        if unit == 'As Displayed':
                                            n_value = float(n_value)/1000000
                                        elif unit == 'In Thousands':
                                            n_value = float(n_value)/1000
                                        #if it was negative add the bracket to signfigy negative
                                        if negative > 0:
                                            n_value = '(' + str(n_value) + ')'
                                        value = n_value
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
                            if str(dict['value']).replace('.','').isdigit():
                                #print(dict)
                                total_dict.append(dict)
                        #if in millions do this
                        else:
                            removelist = "."
                            n_value = re.sub(r'[^\w'+removelist+']', '',value)
                            dict = {}
                            dict['member'] = member
                            dict['header'] = header
                            dict['eng_name'] = eng_name
                            dict['acc_name'] = acc_name
                            dict['value'] = n_value
                            dict['unit'] = 'In Millions'
                            dict['year'] = year
                            dict['report_period'] = report_period
                            dict['statement'] = table
                            dict['filing_type'] = filing_type
                            dict['accession_number'] = accession_number
                            #print(dict)
                            if str(dict['value']).replace('.','').isdigit():
                                #print(dict)
                                total_dict.append(dict)

#print(total_dict)
#All values from this statement have been properly compiled. Time to standardize
scrape_query_2 = "select * from standard_dict where statement = '%s';"%(table)
cursor.execute(scrape_query_2)
johns = cursor.fetchall()
final_standard = []
for john in johns:
    standard_name = john[0]
    acc_name = john[1]
    #print(standard_name, acc_name)
    querys = [item for item in total_dict if item['acc_name'] == acc_name]
    if querys:
        #give current status to the querys
        for query in querys:
            current_year = str(query['year']).split('-',1)[0]
            query['current_year'] = current_year
            query['standard_name'] = standard_name
            query_value = str(query['value'])
            if '(' in query_value:
                query_value = str(query['value']).replace('(','-').replace(')', '')
            if query_value not in query['eng_name']:
                query['eng_name'] = str(query['eng_name'])+'('+query_value+')'
        for query in querys:
            #print(query)
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
                            print('THIS IS THE CURRENT ONE')
                            #print(query)
                            print('L169')
                            #add the names together.
                            if query['acc_name'] not in item['acc_name']:
                                item['acc_name'] = str(item['acc_name']) +", " + str(query['acc_name'])
                            if query['eng_name'] not in item['eng_name']:
                                item['eng_name'] = str(item['eng_name'])+' + '+str(query['eng_name'])
                            #COMPILE THE NUMBERS NOW
                            if '(' in str(item['value']):
                                item['value'] = float(str(item['value']).replace('(','-').replace(')', ''))
                            if '(' in str(query['value']):
                                query['value'] = float(str(query['value']).replace('(','-').replace(')', ''))
                            #compile the values together now. If negative be sure to add the paranthesis back
                            item['value'] = float(item['value']) + float(query['value'])
                            if '-' in str(item['value']):
                                new_val = str(item['value']).replace('-', '')
                                item['value'] = '('+new_val+')'
                                #print(item)
                else:
                    print('THIS DOES NOT EXIST AND WE MUST ADD IT AS THE FIRST OCCURENCE')
                    final_standard.append(query)

            else:
                print('THIS IS NOT COMPOUNDABLE')
                checks = [item for item in final_standard if item['standard_name'] == query['standard_name'] and item['current_year'] == query['current_year'] and item['acc_name'] != query['acc_name']]
                #print(checks)
                if not checks:
                    final_standard.append(query)

print('NOW TALLYING FINAL BUNCH')

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
    print(item['standard_name'], item['acc_name'], item['value'], item['current_year'])
    sql_statement = "INSERT INTO %s (accession_number, header, standard_name, eng_name, acc_name, value, unit, year, statement, report_period, filing_type) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"%(statement_insert, item['accession_number'], item['header'], item['standard_name'], item['eng_name'], item['acc_name'], item['value'], item['unit'], item['year'], item['statement'], item['report_period'], item['filing_type'])
    print(sql_statement)
print(j)
'''


                #if this doesn't exist then append it to the final
                print('IS CHECKS EMPTY?')
                print('THIS IS THE ALREADY EXISTING CHECK')
                print(checks)
                if not checks:
                    print('THIS IS EMPTY')
                    print(checks)
                else:
                    print('CHECKS IS NOT EMPTY L176')
                    print(query)
            else:
                print('NOT COMPOUNDABLE')

                if not checks:
                    print('CHECKS IS EMPTY')
                    query_value = str(query['value'])
                    if '(' in query_value:
                        query_value = str(query['value']).replace('(','-').replace(')', '')
                    query['eng_name'] = str(query['eng_name'])+'('+query_value+')'+'L172 THIS CHECKS IS EMPTY'
                    final_standard.append(query)

                #if this line item exists then append the new value onto it

                    #find the exact item which matches the year, name, and different accounting value in final_standdard
                    for item in final_standard:
                        if item['standard_name'] == query['standard_name'] and item['current_year'] == query['current_year'] and item['acc_name'] != query['acc_name']:
                            #check if eng name and acc_name are in the
                            if '(' in str(item['value']):
                                item['value'] = float(str(item['value']).replace('(','-').replace(')', ''))
                            if '(' in str(query['value']):
                                query['value'] = float(str(query['value']).replace('(','-').replace(')', ''))
                            #compile the values together now. If negative be sure to add the paranthesis back
                            item['value'] = float(item['value']) + float(query['value'])
                            if '-' in str(item['value']):
                                new_val = str(item['value']).replace('-', '')
                                item['value'] = '('+new_val+')'
                            #compile the names in this fashion
                            if query['acc_name'] not in item['acc_name']:
                                item['acc_name'] = str(item['acc_name']) +", " + str(query['acc_name'])
                            if query['eng_name'] not in item['eng_name']:
                                #item['eng_name'] = str(item['eng_name'])+' + '+str(query['eng_name'])+'('+str(query['value'])+')'
                                item['eng_name'] = str(item['eng_name'])+' + '+str(query['eng_name'])
                            print(item)

            #not allowed to compound
            else:
                print('THIS IS NOT COMPOUNDABLE')
'''
                    #compound onto existing check
        #add values that have same standard name and year. Store in Dict with "+" seperating each value


#print('i = ' +str(i))
#
