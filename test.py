import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

year = 'September. 26, 2019'
try:
    if 'Sept' in year:
        year_list = year.split(' ')
        year = year_list[0][0:3] + '. ' + year_list[1] + ' ' + year_list[2]
    year = datetime.strptime(str(year), '%b. %d, %Y')
    year = year.strftime('%Y-%m-%d')
except ValueError:
    try:
        year = datetime.strptime(str(year), '%b %d, %Y')
        year = year.strftime('%Y-%m-%d')
    except ValueError:
        try:
            year = datetime.strptime(str(year), '%B. %d, %Y')
            year = year.strftime('%Y-%m-%d')
        except:
            year = datetime.strptime(str(year), '%B %d, %Y')
            year = year.strftime('%Y-%m-%d')
except:
    continue