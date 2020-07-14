import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import psycopg2

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

cursor.execute("DELETE FROM database.scrape WHERE year=2016;")