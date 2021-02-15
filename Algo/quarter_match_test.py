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

#START OF MAIN PROGRAM BODY
#Grab company
scrape_query = "select * from company;"
cursor.execute(scrape_query)
entries = cursor.fetchall()
#Grab CIK number and then connect it to scrape to get 10-Q
empty = []
total_parse = 0
for entry in entries:
    total_parse+=1
    cik = str(entry[0])
    ticker = str(entry[1])
    print(cik)
    current_year = 2011
    #years completed =
    scrape_query = "select * from scrape where cik_id = '%s' and year = '%s';"%(cik, current_year)
    print(scrape_query)
    cursor.execute(scrape_query)
    filing_entries = cursor.fetchall()
    print(filing_entries)
    q1 = False
    q2 = False
    q3 = False
    for item in filing_entries:
        if item[7] == 'Q1':
            q1 = True
            print('Q1 TRUE')
        if item[7] == 'Q2':
            q2 = True
            print('Q2 TRUE')
        if item[7] == 'Q3':
            q3 = True
            print('Q3 TRUE')
    if q1 == True and q2 == True and q3 == True:
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
                    print('TABLE IS EQUAL TO BALANCE OR IS Q1/Q4')
                    scrape_query = "select * from %s where accession_number = '%s' and date_part('year', year) = '%s';"%(table, accession_number, current_year)
                #scrape_query = "select * from %s where accession_number = '%s';"%(table, accession_number)
                print(scrape_query)
                cursor.execute(scrape_query)
                smiths = cursor.fetchall()
                if not smiths:
                    print('THIS ACCESSION NUMBER HAS NOTHING')
                    print(accession_number)
                    empty.append(accession_number)
                else:
                    print('THIS ACCESSION NUMBER HAS EVERYTHING')
