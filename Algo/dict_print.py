#GRABS ALL THE STANDARD DICTS, THEN COMPILES THEM SO HUMANS CAN SORT AND CLEAN THEM BY HAND
import re
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import psycopg2
import os
from itertools import groupby
from operator import itemgetter
from docx.enum.text import WD_COLOR_INDEX
from docx import Document

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

scrape_query = "select * from standard_dict;"
cursor.execute(scrape_query)
entries = cursor.fetchall()

document = Document()

copy = []
for entry in entries:
    dict = {}
    dict['standard_name'] = entry[0]
    dict['acc_name'] = entry[1]
    copy.append(dict)

seen = set()
new_l = []
for d in copy:
    t = tuple(d.items())
    if t not in seen:
        seen.add(t)
        new_l.append(d)

s = 0
k = itemgetter('standard_name')
i = groupby(sorted(new_l, key=k), key=k)
for key, new_l in i:
    s+=1
    header = str(key)
    document.add_paragraph(header)
    for item in new_l:
        smith = str(item)
        document.add_paragraph(smith)

print(s)
document.save('docx_file.docx')
