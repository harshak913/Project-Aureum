import requests
import urllib
import datetime
import os
from bs4 import BeautifulSoup
import psycopg2
from Inter_Table import interParse

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

def delete_from_tables(accession_number):
    cursor.execute("DELETE FROM database.balance WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM database.income WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM database.cash_flow WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM database.non_statement WHERE accession_number='%s'"%(accession_number))

def check_if_incomplete(accession_number):
    cursor.execute("SELECT * FROM database.balance WHERE accession_number='%s';"%(accession_number))
    balance_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM database.income WHERE accession_number='%s';"%(accession_number))
    income_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM database.cash_flow WHERE accession_number='%s';"%(accession_number))
    cash_flow_entry = cursor.fetchall()
    if len(balance_entry) == 0 or len(income_entry) == 0 or len(cash_flow_entry) == 0:
        return True
    else:
        return False

years = list(range(2015, 2016))

for year in years:
    complete = False
    while complete == False:
        cursor.execute("SELECT * FROM database.scrape WHERE status='INCOMPLETE' AND year=%s;"%(year))
        unfinished_list = cursor.fetchall()

        if len(unfinished_list) == 0:
            complete = True
            break

        for unfinished in unfinished_list:
            print(unfinished)
            accession_number = unfinished[4]
            filing_type = unfinished[1]
            index_url = unfinished[3].strip('.txt') + '-index.htm'

            try:
                interParse(index_url, accession_number, filing_type)
                if check_if_incomplete(accession_number):
                    print(f"Did not parse this completely, URL:{index_url}")
                    delete_from_tables(accession_number)
                    continue
                else:
                    cursor.execute("UPDATE database.scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession_number))
                    print(f"Parsed successfully & updated status to COMPLETED, URL: {index_url}")
            except:
                print(f"Something went wrong, URL: {index_url}")
                delete_from_tables(accession_number)
