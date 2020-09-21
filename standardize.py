import re
import csv
import psycopg2
import os

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

final_dict = []

cursor.execute("SELECT * FROM dictionary;")
entries = cursor.fetchall()

#GRAB ALL ITEMS FROM DICTIONARY
for entry in entries:
    stand_name = str(entry[0])
    eng_name = str(entry[1])
    acc_name = str(entry[2])
    statement = str(entry[3])
    #SELECT THE ROWS THAT DON'T HAVE THIS GAAP TAG BUT HAS THIS ENG_NAME
    sql_line = "SELECT * FROM %s WHERE upper(acc_name) != '%s'  and member = '' and upper(eng_name) = '%s';"%(statement, acc_name.upper(), eng_name.upper())
    print(sql_line)
    cursor.execute(sql_line)
    tables = cursor.fetchall()
    all_variations = []
    for table in tables:
        if str(table[4]) != '':
            all_variations.append(str(table[4]))

    #REMOVE DUPLICATES
    seen = set()
    cleaned_acc = []
    for item in all_variations:
        t = tuple(item)
        if t not in seen:
            seen.add(t)
            cleaned_acc.append(item)

    for item in cleaned_acc:
        the_item = str(item)
        sql_command = "SELECT * FROM standard_dict where standard_name = '%s' and acc_name = '%s'"%(stand_name, the_item)
        cursor.execute(sql_command)
        entries = cursor.fetchall()
        if not entries:
            #print(the_item)
            sql_command = "INSERT INTO standard_dict (standard_name ,acc_name, statement) VALUES('%s', '%s', '%s');"%(stand_name ,the_item, statement)
            print(sql_command)
            cursor.execute(sql_command)

"""
cursor.execute("SELECT * FROM public.standard_dict where standard_name = 'Net Income' and acc_name = 'ZooWeeMama'")
entries = cursor.fetchall()
if not entries:
    print(' Does NOT EXISTS')


seen = set()
cleaned_eng = []
for item in eng_names:
    t = tuple(item)
    if t not in seen:
        seen.add(t)
        cleaned_eng.append(item)
"""
