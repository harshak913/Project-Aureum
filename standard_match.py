import re
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import psycopg2
import os

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

scrape_query = "select * from scrape where filing_type = '10-K' and inter_or_htm = 'Inter' and year = '2011';"
cursor.execute(scrape_query)
entries = cursor.fetchall()
tables = ['balance','cash_flow','income']

#grab all accession numbers for 10-Ks in this year
for entry in entries:
    accession_number = str(entry[4])
    for table in tables:
        #grab the balance, cash or income table and match it with the accession_number
        scrape_query = "select * from %s where accession_number = '%s';"%(table, accession_number)
        #time to go through the table
        for item in scrape_query:
            member = str(entry[1])
            header = str(entry[2])
            eng_name = str(entry[3])
            acc_name = str(entry[4])
            value = str(entry[5])
            unit = str(entry[6])
            #make sure that it's not a member
            if '[' not in member:
                if 'MEMBER' not in member.upper():
                    #must take into account negative value of numbers
                    negative = False
                    if "(" or '-' in value:
                        negative = True
                    #unit conversion from thousand and as displayed to millions
                    if unit == 'As Displayed':
                        value = value.split()
                    elif unit == 'In Thousand':
                        value =
