from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Prefetch
from .models import Balance, CashFlow, Income, NonStatement, Company
from .forms import MyForm
from operator import itemgetter
from itertools import groupby
import datetime
import json
import urllib.request
from bs4 import BeautifulSoup
import re
# Create your views here.
# Link to actual SEC site https://www.sec.gov/cgi-bin/viewer?action=view&cik=1067983&accession_number=0001193125-10-043450&xbrl_type=v#
"""
statement_list = ['CashFlow','Income','Balance']
for item in statement_list:
    if item == 'Balance':
        bal_years =  Balance.objects.values('year').distinct().order_by('year')
        bal_years = list(bal_years)
        bal_key = itemgetter('year')
        bal_iter = groupby(sorted(bal_years, key=bal_key), key=bal_key)
        bal_dates = []
        for year, bal_years in bal_iter:
            bal_dates.append(year)
        bal_years = []
        for date in bal_dates:
            bal_years.append(date.year)
        bal_min = min(bal_years)
        bal_max = max(bal_years)

    elif item == 'Income':
        inc_years =  Income.objects.values('year').distinct().order_by('year')
        inc_years = list(inc_years)
        inc_key = itemgetter('year')
        inc_iter = groupby(sorted(inc_years, key=inc_key), key=inc_key)
        inc_dates = []
        for year, inc_years in inc_iter:
            inc_dates.append(year)
        inc_years = []
        for date in inc_dates:
            inc_years.append(date.year)
        inc_min = min(inc_years)
        inc_max = max(inc_years)

    elif item == 'CashFlow':
        cash_years =  CashFlow.objects.values('year').distinct().order_by('year')
        cash_years = list(cash_years)
        cash_key = itemgetter('year')
        cash_iter = groupby(sorted(cash_years, key=cash_key), key=cash_key)
        cash_dates = []
        for year, cash_years in cash_iter:
            cash_dates.append(year)
        cash_years = []
        for date in cash_dates:
            cash_years.append(date.year)
        cash_min = min(cash_years)
        cash_max = max(cash_years)
"""
#NEWS ARTICLE CATCHING

urls = ['https://www.cnbc.com/finance/','https://www.cnn.com/business/investing','https://www.foxbusiness.com/markets']
articles = []
for url in urls:
    if 'cnbc' in url:
        link_head = 'cnbc.com'
    elif 'foxbusiness'in url:
        link_head = 'foxbusiness.com'
    elif 'cnn'in url:
        link_head = 'cnn.com'
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, features="lxml")
    i = 0
    if soup.find('article') is not None:
        for item in soup.find_all('article'):
            if i != 5:
                art_dict = {}
                anchor = item.find('a')
                title = item.find(re.compile('^h[1-6]$'))
                if link_head not in anchor['href']:
                    full_link = link_head + anchor['href']
                else:
                    full_link = anchor['href']
                #print(title.text, full_link)
                art_dict['title'] = title.text
                if 'www' not in full_link:
                    art_dict['link'] = 'https://www.'+full_link
                else:
                    art_dict['link'] = full_link
                articles.append(art_dict)
                i+=1

            else:
                break
    elif soup.find("a", {"class":"Card-title"}) is not None:
        for item in soup.find_all("a", {"class":"Card-title"}):
            if i != 5:
                art_dict = {}
                if link_head not in item['href']:
                    full_link = link_head + item['href']
                else:
                    full_link = item['href']
                #print(item.text, full_link)
                art_dict['title'] = item.text
                if 'www' not in full_link:
                    art_dict['link'] = 'https://www.'+full_link
                else:
                    art_dict['link'] = full_link
                articles.append(art_dict)
                i+=1
            else:
                break
#END OF REORGANAZTION
new_list = Company.objects.values('name', 'ticker', 'cik')
list = []
for item in new_list:
    list.append(item['name'])
    list.append(item['ticker'])


companies = json.dumps(list)

def home(request):
    context = {
        'Companies': companies,
        'Articles': articles
    }
    return render(request, 'aureum/home.html', context)

def information(request):
    myCountry = request.GET.get('myCountry')
    for item in new_list:
        if item['ticker'] == myCountry or item['name'] == myCountry:
            myCountry = item['name']
    #if the form request is not None, set the session to the current entered one
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    context = {
        'Company': myCountry,
        'Companies': companies
    }
    return render(request, 'aureum/information.html', context)

def balance(request):
    myCountry = request.GET.get('myCountry')
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    context = {
        'Datas': Balance.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year').distinct().order_by('year'),
        'Max': bal_max,
        'Min': bal_min,
        'Curr_Max': bal_max,
        'Curr_Min': bal_min,
        'Company': myCountry,
        'Companies': companies,
        'Statement': 'Balance Sheet'
    }
    return render(request, 'aureum/base.html', context)

def income(request):
    myCountry = request.GET.get('myCountry')
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    context = {
        'Datas': Income.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year').distinct().order_by('year'),
        'Max': inc_max,
        'Min': inc_min,
        'Curr_Max': inc_max,
        'Curr_Min': inc_min,
        'Company': myCountry,
        'Companies': companies,
        'Statement': 'Income Statement'
    }
    return render(request, 'aureum/base.html', context)



def cash(request):
    myCountry = request.GET.get('myCountry')
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    if year1 is not None:
        context = {
            'Datas': CashFlow.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year').distinct().order_by('year').filter(year__year__range=(year1, year2)),
            'Max': cash_max,
            'Min': cash_min,
            'Curr_Min': year1,
            'Curr_Max': year2,
            'Company': myCountry,
            'Companies': companies,
            'Statement': 'Cash Flow'
            }
    else:
        context = {
            'Datas': CashFlow.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year').distinct().order_by('year'),
            'Max': cash_max,
            'Min': cash_min,
            'Curr_Min': cash_min,
            'Curr_Max': cash_max,
            'Company': myCountry,
            'Companies': companies,
            'Statement': 'Cash Flow'
            }
    return render(request, 'aureum/base.html', context)
