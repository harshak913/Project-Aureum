import requests
import urllib
import datetime
import os
from bs4 import BeautifulSoup
import psycopg2
import xml.etree.ElementTree as ET
from Inter_Table import interParse

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

cursor.execute("SELECT cik FROM database.company;")
ciks = cursor.fetchall()

years = list(range(2016, 2017))

for year in years:
    for cik in ciks:
        cursor.execute("SELECT * FROM database.scrape WHERE cik_id=%s AND year=%s;"%(cik[0], year))
        results = cursor.fetchall() # Sequence of tuples inside a list for each CIK (each tuple is info from scrape table for a filing)
        num10K = num10Q = 0