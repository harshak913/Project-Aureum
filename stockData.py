import yfinance as yf
import psycopg2
import pandas as pd
import csv
import os
import datetime

# Stock data collection
connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

""" cursor.execute("SELECT cik, ticker FROM company ORDER BY ticker ASC;")
companies = cursor.fetchall()

cursor.execute("SELECT DISTINCT cik FROM stock_data;")
ciks = cursor.fetchall()
cikList = []
for cik in ciks:
    cikList.append(cik[0])

for company in companies:
    if company[0] in cikList:
        print(f'{company[0]}, {company[1]} Already inserted in stock table')
        continue
    
    if company[0] in (0, 1, 2, 3, 4, 5, 6):
        continue

    ticker = company[1]
    frequencyCounter = 0

    #Collect data for 1 day
    df = yf.download(f'{ticker}', period='1d', interval='1m')

    if df.empty:
        continue
    
    df.to_csv(f'{ticker}.csv')

    #Collect data for 5 days
    df = yf.download(f'{ticker}', period='5d', interval='30m')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    #Collect data for 1 month
    df = yf.download(f'{ticker}', period='1mo', interval='1d')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    #Collect data for 1 year
    df = yf.download(f'{ticker}', period='1y', interval='1d')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    #Collect data for 5 years
    df = yf.download(f'{ticker}', period='5y', interval='1wk')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    csvfile = open(f'{ticker}.csv', 'r')
    reader = csv.reader(csvfile)
    for row in reader:
        if 'Date' in row[0]:
            frequencyCounter += 1
            continue

        if row[1] == '':
            continue

        dateList = row[0].split()
        date = dateList[0] + ' ' + dateList[1].split('-')[0] if len(dateList) == 2 else dateList[0]

        if frequencyCounter == 1:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '1d', '1m')"%(company[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 2:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '5d', '30m')"%(company[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 3:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '1mo', '1d')"%(company[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 4:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '1y', '1d')"%(company[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 5:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '5y', '1wk')"%(company[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
    
    csvfile.close()
    print(f'Done with {ticker}.csv')
        
    try:
        os.remove(f'{ticker}.csv')
        print("SUCCESSFULLY REMOVED FILES\n")
    except OSError as e:
        print(f"FAILED TO REMOVE FILES: {e}\n") """

# Index data collection
cursor.execute("SELECT cik, ticker FROM company WHERE cik=7 OR cik=8 OR cik=9;")

indices = cursor.fetchall()

for index in indices:
    ticker = index[1]

    #Collect data for 1 day
    df = yf.download(f'{ticker}', period='1d', interval='1m')
    df.to_csv(f'{ticker}.csv')

    #Collect data for 5 days
    df = yf.download(f'{ticker}', period='5d', interval='30m')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    #Collect data for 1 month
    df = yf.download(f'{ticker}', period='1mo', interval='1d')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    #Collect data for 1 year
    df = yf.download(f'{ticker}', period='1y', interval='1d')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    #Collect data for 5 years
    df = yf.download(f'{ticker}', period='5y', interval='1wk')
    df.to_csv(f'{ticker}.csv', mode='a', header=True)

    frequencyCounter = 0

    csvfile = open(f'{ticker}.csv', 'r')
    reader = csv.reader(csvfile)
    for row in reader:
        if 'Date' in row[0]:
            frequencyCounter += 1
            continue

        if row[1] == '':
            continue

        dateList = row[0].split()
        date = dateList[0] + ' ' + dateList[1].split('-')[0] if len(dateList) == 2 else dateList[0]

        if frequencyCounter == 1:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '1d', '1m')"%(index[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 2:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '5d', '30m')"%(index[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 3:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '1mo', '1d')"%(index[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 4:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '1y', '1d')"%(index[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))
        elif frequencyCounter == 5:
            cursor.execute("INSERT INTO stock_data (cik, date, open, high, low, close, adj_close, volume, period, interval) VALUES (%s, '%s', %s, %s, %s, %s, %s, %s, '5y', '1wk')"%(index[0], date, row[1], row[2], row[3], row[4], row[5], row[6]))

    csvfile.close()
    print(f'Done with {ticker}.csv')
        
    try:
        os.remove(f'{ticker}.csv')
        print("SUCCESSFULLY REMOVED FILES\n")
    except OSError as e:
        print(f"FAILED TO REMOVE FILES: {e}\n")


# Additional stock info (company table)
""" cursor.execute("SELECT cik, ticker FROM company ORDER BY ticker ASC;")
companies = cursor.fetchall()

for company in companies:
    ticker = yf.Ticker(f'{company[1]}')

    cursor.execute("SELECT * FROM stock_data WHERE cik=%s AND period='1d' ORDER BY date ASC;"%(company[0]))
    results = cursor.fetchall()

    if len(results) == 0:
        continue

    open = results[0][2]

    date = results[0][1]
    date = date.strftime('%Y-%m-%d')
    if '06-10' in date:
        df = yf.download(f'{company[1]}', start='2021-06-09', end='2021-06-10')
        df2 = yf.download(f'{company[1]}', start='2021-06-10', end='2021-06-11')
    else:
        df = yf.download(f'{company[1]}', start='2021-06-10', end='2021-06-11')
        df2 = yf.download(f'{company[1]}', start='2021-06-11', end='2021-06-12')
    
    df.to_csv(f'{company[1]}.csv', mode='a', header=False)
    df2.to_csv(f'{company[1]}.csv', mode='a', header=False)

    csvfile = open(f'{company[1]}.csv', 'r')
    reader = csv.reader(csvfile)

    data = []
    for row in reader:
        data.append(row)
    
    csvfile.close()
    print(data)


    cursor.execute("SELECT * FROM stock_data WHERE cik=%s AND period='1d' ORDER BY high DESC;"%(company[0]))
    day_high = cursor.fetchall()[0][3]

    cursor.execute("SELECT * FROM stock_data WHERE cik=%s AND period='1d' ORDER BY low ASC;"%(company[0]))
    day_low = cursor.fetchall()[0][4]

    cursor.execute("SELECT * FROM stock_data WHERE cik=%s AND period='1y' ORDER BY high DESC;"%(company[0]))
    year_high = cursor.fetchall()[0][3]

    cursor.execute("SELECT * FROM stock_data WHERE cik=%s AND period='1y' ORDER BY low ASC;"%(company[0]))
    year_low = cursor.fetchall()[0][4]

    market_cap = ticker.info['marketCap']
    volume = ticker.info['averageVolume10days']

    insert_statement = "UPDATE company SET open=%s, avg_volume_10_days=%s, day_high=%s, day_low=%s, year_high=%s, year_low=%s, market_cap=%s WHERE cik=%s;"%(open, volume, day_high, day_low, year_high, year_low, market_cap, company[0])

    cursor.execute(insert_statement)
    print(insert_statement) """

# Add code for prev_close