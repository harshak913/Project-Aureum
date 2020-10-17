import re
import csv
import psycopg2
import os
import os.path

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()
"""
cursor.execute("SELECT * FROM dictionary;")
entries = cursor.fetchall()
for entry in entries:
    if entry[1] is None:
        dict_acc = str(entry[2]).upper()
        stand_name = str(entry[1])
        statements = ['income','cash_flow','balance']
        for statement in statements:
            cursor.execute("SELECT * FROM %s WHERE upper(acc_name) = '%s'  and member = '';")%(statement, dict_acc)
            tables = cursor.fetchall()
            for table in tables:

csvfile = open('dictionary.csv', 'r')
reader = csv.DictReader(csvfile)
rows = list(reader)
dicts = []


for row in rows:
    john = row.items()
    for key, value in john:
        if key == 'standard':
            english = value
        if key == 'accounting':
            account = value
        if key == 'statement':
            statement = value
            if statement == "IS":
                statement = "income"
            elif statement == "CS":
                statement = "cash_flow"
            elif statement == "BS":
                statement = "balance"
            #if ':' in value:
            #    account = value.rsplit(':',1)[1]
            #elif value != '':
    dict={}
    dict['standard'] = english
    dict['account'] = account
    dict['statement'] = statement
    dicts.append(dict)
    #print(english, account)
new_dict = []
for item in dicts:
    if item['standard'] != '' and item['account'] != '':
        new_dict.append(item)

for item in new_dict:
    smith = str(item['account']).rsplit(':',1)[1]
    item['account'] = smith


seen = set()
new_l = []
for item in new_dict:
    t = tuple(item.items())
    if t not in seen:
        seen.add(t)
        new_l.append(item)
"""

#CREATE THE STATEMENT DICT
csvfile = open('StatementLinks.csv', 'r')
reader = csv.DictReader(csvfile)
rows = list(reader)
dicts = []


for row in rows:
    john = row.items()
    for key, value in john:
        if key == 'standard':
            english = value
        if key == 'statement':
            statement = value
            if statement == "IS":
                statement = "income"
            elif statement == "CS":
                statement = "cash_flow"
            elif statement == "BS":
                statement = "balance"
            #if ':' in value:
            #    account = value.rsplit(':',1)[1]
            #elif value != '':
    dict={}
    dict['standard'] = english
    dict['statement'] = statement
    dicts.append(dict)

stand_dict = []

total_items = 0

for dict in dicts:
    if dict['standard'] != '':
        #total_items+=1
        stand_dict.append(dict)

for dict in stand_dict:
    total_items+=1
    stand_name = dict['standard']
    statement = dict['statement']
    sql_command = "SELECT * FROM standard_dict where standard_name = '%s'"%(stand_name)
    cursor.execute(sql_command)
    entries = cursor.fetchall()
    cleaned_stand = re.sub(r'\W+', '', stand_name).replace(" ", "_")
    filename = "/Users/octavian/Desktop/Project-Aureum/%s/%s.csv"%(statement,cleaned_stand)
    print(filename)
    #filename = "/Users/Harsh/OneDrive - The University of Texas at Dallas/Documents/Project A/HTM/%s.xml"%(doc_name)
    #for entry in entries:
    #    print(entry[1])

#print('Total Items: ' + str(total_items))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["standard", "gaap_tag", "statement"])
        for entry in entries:
            writer.writerow([entry[0], entry[1], entry[2]])

'''
for dict in stand_dict:
    print(dict)
    john = str(re.sub(r'\W+', '', str(dict['standard']))).upper()
    print('CONTRACTED NAME: '+ john)
'''

"""
final_dicts = []

for item in new_l:
    standard = str(item.get('standard'))
    account = str(item.get('account'))
    og_stat = str(item.get('statement'))
    statement = ''
    for dict in stand_dict:
        dict_name = str(dict['standard'])
        dict_stat = str(dict['statement'])
        test_name = str(re.sub(r'\W+', '', str(dict_name))).upper()
        curr_name = str(re.sub(r'\W+', '', str(standard))).upper()
        if curr_name == test_name:
            standard = dict_name
            statement = dict_stat
        #print("THESE STANDARDS HAVE NO STATEMENTS: " + standard + " ACCOUNTING NAME: "+ account)
        #print("^ORIGINAL STATEMENT: "+og_stat)
    if statement != '':
        fin_dict = {}
        #sql_statement = "INSERT INTO dictionary (standard_name, acc_name, statement) VALUES('%s', '%s', '%s');"%(standard, account, statement)
        fin_dict['standard'] = standard
        fin_dict['account'] = account
        fin_dict['statement'] = statement
        final_dicts.append(fin_dict)
        #print(sql_statement)

seen = set()
new_l = []
for item in final_dicts:
    t = tuple(item.items())
    if t not in seen:
        seen.add(t)
        new_l.append(item)

for dict in new_l:
    standard = dict['standard']
    account = dict['account']
    statement = dict['statement']
    sql_statement = "INSERT INTO standard_dict (standard_name ,acc_name, statement) VALUES('%s', '%s', '%s');"%(standard ,account, statement)
    print(sql_statement)
    cursor.execute(sql_statement)

for dict in final_dicts:
    statement = dict['statement']
    account = str(dict['account']).upper()
    #access where all eng names with that accounting name
    sql_line = ("SELECT * FROM %s WHERE upper(acc_name) = '%s'  and member = '';")%(statement, account)
    #cursor.execute("SELECT * FROM %s WHERE upper(acc_name) = '%s'  and member = '';")%(statement, account)
    cursor.execute(sql_line)
    tables = cursor.fetchall()
    eng_names = []
    for table in tables:
        eng_names.append(table[3])
    #remove duplicate names
    seen = set()
    cleaned_eng = []
    for item in eng_names:
        t = tuple(item)
        if t not in seen:
            seen.add(t)
            cleaned_eng.append(item)
    #Time to create a dict of all the eng name and standard variations
    standard = dict['standard']
    account = dict['account']
    statement = dict['statement']
    final_dict = []
    for item in cleaned_eng:
        dict = {}
        dict['eng_name'] = item
        dict['standard'] = standard
        dict['account'] = account
        dict['statement'] = statement
        final_dict.append(dict)
    #NOW WE HAVE THE COMPLETE DICTIONARY FOR THIS SPECIFIC STANDARD NAME AND ACCOUNTING NAME
    for item in final_dict:
        eng_name = item['eng_name']
        standard = item['standard']
        account = item['account']
        statement = item['statement']
        sql_statement = "INSERT INTO dictionary (standard_name, eng_name ,acc_name, statement) VALUES('%s', '%s', '%s', '%s');"%(standard, eng_name ,account, statement)
        print(sql_statement)
        cursor.execute(sql_statement)
"""
# and upper(eng_name) = 'NETINCOMELOSS' and member = ''
#SELECT * FROM income WHERE upper(acc_name) = 'NETINCOMELOSS';
