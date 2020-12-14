import re
import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, NavigableString
import os
import xml.etree.ElementTree as ET
import requests
'''
#BLOOMBERG ARTICLE <article class="story-package-module__story mod-story" data-id="QL6SHET0G1LD01" data-tracking-type="Story" data-updated-at="2020-12-12T19:21:42.621Z" data-type="article">
url = 'https://www.bloomberg.com/markets'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
page = urlopen(req).read()
soup = BeautifulSoup(page, features="lxml")
news = soup.find_all("a", {"class": "story-package-module__story__headline-link"})
i = 0
for new in news:
    i+=1
    link = 'https://www.bloomberg.com' + str(new['href'])
    title = str(new.text).strip()
    #print(title, link)


#WSJ ARTICLE FORMAT
url = 'https://www.wsj.com/news/business'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
page = urlopen(req).read()
soup = BeautifulSoup(page, features="lxml")

news = soup.find_all("h3", {"class": 'WSJTheme--headline--unZqjb45 reset WSJTheme--heading-5--1oh0iDBS typography--serif--1CqEfjrc'})
for new in news:
    links = new.findChildren('a')
    for link in links:
        href = link['href']
        title = link.text
        #print(title, href)

#CNBC Format
url = 'https://www.cnbc.com'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
page = urlopen(req).read()
soup = BeautifulSoup(page, features="lxml")
news = soup.find_all('div', {"class": 'RiverHeadline-headline RiverHeadline-hasThumbnail'})
i = 0
for new in news:
    links = new.findChildren('a')
    for link in links:
        href = link['href']
        title = link.text
        #print(title, href)
'''
#CONGLOMERATE
all_art = []
urls = ['https://www.bloomberg.com/markets','https://www.wsj.com/news/business','https://www.cnbc.com']
for url in urls:
    if 'bloomberg' in url:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
        soup = BeautifulSoup(page, features="lxml")
        news = soup.find_all("a", {"class": "story-package-module__story__headline-link"})
        for new in news:
            dict = {}
            link = 'https://www.bloomberg.com' + str(new['href'])
            title = str(new.text).strip()

            print(title, link)

    else:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
        soup = BeautifulSoup(page, features="lxml")

        if 'cnbc' in url:
            news = soup.find_all('div', {"class": 'RiverHeadline-headline RiverHeadline-hasThumbnail'})
        elif 'wsj' in url:
            news = soup.find_all("h3", {"class": 'WSJTheme--headline--unZqjb45 reset WSJTheme--heading-5--1oh0iDBS typography--serif--1CqEfjrc'})

        for new in news:
            links = new.findChildren('a')
            for link in links:
                dict = {}
                href = link['href']
                title = link.text
                print(title, href)

'''
COMPANY SPECIFIC SEARCH

URL="https://finviz.com/quote.ashx?t=%s"%('aapl')
print(URL)

req = Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
page = urlopen(req).read()
#page = urllib.request.urlopen(URL).read()
soup = BeautifulSoup(page, features="lxml")
#print(soup.prettify())
news = soup.find_all("div", {"class": "news-link-container"})
all_news = []
for new in news:
    single = {}
    titles = new.findChildren("div", {"class": "news-link-left"})
    for title in titles:
        links = title.findChildren('a')
        for link in links:
            single['single'] = link['href']
        single['title'] = title.text
    sources = new.findChildren("div", {"class": "news-link-right"})
    for source in sources:
        single['source'] = source.text
    print(single)

'''
