import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import psycopg2

conn = psycopg2.connect(host="ec2-34-233-226-84.compute-1.amazonaws.com", dbname="d77knu57t1q9j9", user="jsnmfiqtcggjyu", password="368e05099543272efb167e9fa3173338be43c1e787666ed2478f51ef050707b9")
conn.autocommit = True
cursor = conn.cursor()

cursor.execute("DELETE FROM database.scrape WHERE filing_type='10-Q';")