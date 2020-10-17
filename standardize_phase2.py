import re
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import psycopg2
import os

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

file_list = ['V1_StandBal.xlsx','V1_StandCash.xlsx','V1_StandIncome.xlsx']

total_count = 0

for item in file_list:
    df = pd.read_excel(item)
    for index, row in df.iterrows():
        total_count+=1
        standard = row['standard']
        acc_name = row['gaap_tag']
        statement = row['statement']
        sql_command = "INSERT INTO standard_dict (standard_name ,acc_name, statement) VALUES('%s', '%s', '%s');"%(standard ,acc_name, statement)
        print(sql_command)

print('Total Rows: '+str(total_count))
