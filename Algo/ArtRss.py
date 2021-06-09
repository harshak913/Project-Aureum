import feedparser
import psycopg2
import re

connection = psycopg2.connect(host="ec2-34-197-188-147.compute-1.amazonaws.com", dbname="d7p3fuehaleleo", user="snbetggfklcniv", password="7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a")
connection.autocommit = True
cursor = connection.cursor()

#company specific news------------->
scrape_query = "select * from company;"
cursor.execute(scrape_query)
entries = cursor.fetchall()

for entry in entries:
    if entry[0] != 0:
        ticker = entry[1]
        #name = re.sub(r'\W+', '', entry[2])
        cik = entry[0]
        #if cik == 315189:
        #    breakOff = True
        #print(name)
        #newsQ = "https://news.google.com/rss/search?q="+name+"ticker&hl=en-US&gl=US&ceid=US%3Aen"
        newsQ = "https://news.google.com/rss/search?q="+ticker+"-ticker&hl=en-US&gl=US&ceid=US%3Aen"
        NewsFeed = feedparser.parse(newsQ) #company specific
        #print(NewsFeed)
        i=0
        for item in NewsFeed['entries']:
            if i < 50:
                title =item['title'].replace("'", "‘")
                link = item['link'].replace("'", "‘")
                date_published = item['published']
                source = item['source']['title'].replace("'", "‘")
                i+=1
                sql_statement = "INSERT INTO news (cik, title, link, date_published, source) VALUES('%s', '%s', '%s', '%s', '%s')"%(cik, title, link, date_published, source)
                print(sql_statement)
                #cursor.execute(sql_statement)

    #print(i)
allCats = [
#Business News ------------------------>DONE
{'NewsFeed': "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen" #general business news
,'cik': 0},

#US News-------------------------->DONE
{'NewsFeed': 'https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE?hl=en-US&gl=US&ceid=US%3Aen'
,'cik': 1},

#World News----------------------->
{'NewsFeed': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen'
,'cik': 2},

#Technology News------------------>
{'NewsFeed': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen'
,'cik': 3},

#Entertainment News--------------->
{'NewsFeed': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen'
,'cik': 4},

#Science News------------------------->
{'NewsFeed': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen'
,'cik': 5},

#Health News---------------------->
{'NewsFeed': 'https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-US&gl=US&ceid=US%3Aen'
,'cik': 6},
]

for cats in allCats:
    NewsFeed = feedparser.parse(cats['NewsFeed'])
    cik = cats['cik']
    for item in NewsFeed['entries']:
        title =item['title'].replace("'", "‘")
        link = item['link']
        date_published = item['published']
        source = item['source']['title'].replace("'", "‘")
        sql_statement = "INSERT INTO news (cik, title, link, date_published, source) VALUES('%s', '%s', '%s', '%s', '%s')"%(cik, title, link, date_published, source)
        print(sql_statement)
        #cursor.execute(sql_statement)
