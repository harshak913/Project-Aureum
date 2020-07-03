import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

text_filing = "https://www.sec.gov/Archives/edgar/data/764478/000110465902000013/0001104659-02-000013.txt"
response = requests.get(text_filing)
soup = BeautifulSoup(response.content, 'lxml')
if '.htm' in soup.find_all("filename")[0].get_text():
    print("hehe")