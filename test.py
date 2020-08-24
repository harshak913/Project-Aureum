import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from HTMLFinal import HTMLParse

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

def delete_from_tables(accession_number):
    cursor.execute("DELETE FROM balance WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM income WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM cash_flow WHERE accession_number='%s'"%(accession_number))
    cursor.execute("DELETE FROM non_statement WHERE accession_number='%s'"%(accession_number))

def check_if_incomplete(accession_number):
    cursor.execute("SELECT * FROM balance WHERE accession_number='%s';"%(accession_number))
    balance_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM income WHERE accession_number='%s';"%(accession_number))
    income_entry = cursor.fetchall()

    cursor.execute("SELECT * FROM cash_flow WHERE accession_number='%s';"%(accession_number))
    cash_flow_entry = cursor.fetchall()

    return (len(balance_entry) == 0 or len(income_entry) == 0 or len(cash_flow_entry) == 0)

cursor.execute("SELECT * FROM scrape WHERE year=2010 AND inter_or_htm='HTM';")
results = cursor.fetchall()
for result in results:
    print(result)
    index_page = result[3].strip('.txt') + "-index.htm"
    accession_number = result[4]
    response = requests.get(index_page)
    soup = BeautifulSoup(response.content, 'lxml')
    period_of_report = soup.find('div', text='Period of Report').find_next_sibling('div').text

    try:
        print(f"PARSING {result[3]} NOW")
        HTMLParse(result[3], '10k', accession_number, result[1], period_of_report)

        if check_if_incomplete(accession_number):
            sql_statement = "UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s';"%(accession_number)
            cursor.execute(sql_statement)
            print(sql_statement)
            delete_from_tables(accession_number)
        else:
            sql_statement = "UPDATE scrape SET status='COMPLETED' WHERE accession_number='%s';"%(accession_number)
            cursor.execute(sql_statement)
            print(sql_statement)
    except:
        if os.path.exists('10k-balance_sheet.csv'):
            os.remove('10k-balance_sheet.csv')
        if os.path.exists('10k-income_statement.csv'):
            os.remove('10k-income_statement.csv')
        if os.path.exists('10k-cash_flows.csv'):
            os.remove('10k-cash_flows.csv')
        delete_from_tables(accession_number)
        sql_statement = "UPDATE scrape SET status='INCOMPLETE' WHERE accession_number='%s'"%(accession_number)
        cursor.execute(sql_statement)
        print(sql_statement)

""" cursor.execute("SELECT * FROM scrape WHERE year=2002 AND status='INCOMPLETE';")
results = cursor.fetchall()
for result in results:
    accession_number = result[4]
    delete_from_tables(accession_number)
    cursor.execute("UPDATE scrape SET status='PENDING' WHERE accession_number='%s'"%(accession_number)) """