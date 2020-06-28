import xml.etree.ElementTree as ET
import requests

url_xml = 'https://www.sec.gov/Archives/edgar/data/764478/000110465902000013/FilingSummary.xml'
tree = ET.fromstring(requests.get(url_xml).text)
if tree[0].text == 'NoSuchKey':
    print("Error")