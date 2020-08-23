from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Prefetch
from .models import Balance, CashFlow, Income, NonStatement, Company, Scrape
from .forms import MyForm
import itertools
from operator import itemgetter
from itertools import groupby
import datetime
import json
import urllib.request
from bs4 import BeautifulSoup
import re
# Create your views here.
# Link to actual SEC site https://www.sec.gov/cgi-bin/viewer?action=view&cik=1067983&accession_number=0001193125-10-043450&xbrl_type=v#
#NEWS ARTICLE CATCHING
#def year_cleanup(data_set, all_years):
#    bal_key = itemgetter('member')
#    bal_iter = groupby(sorted(theBalance, key=bal_key), key=bal_key)
'''
Balances = Balance.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year__year').filter(accession_number__in=['0001393612-12-000008', '0001193125-11-014919', '0001393612-16-000059', '0001393612-13-000004', '0001393612-14-000012', '0001393612-15-000007', '0001393612-17-000012', '0001393612-18-000012', '0001393612-19-000011']).distinct()
#print(Balances)
Balances = list(Balances)

marks = list(Balances)
johns = list(Balances)
insert = []

bal_years =  Balance.objects.values('year__year').filter(accession_number__in=['0001393612-12-000008', '0001193125-11-014919', '0001393612-16-000059', '0001393612-13-000004', '0001393612-14-000012', '0001393612-15-000007', '0001393612-17-000012', '0001393612-18-000012', '0001393612-19-000011']).distinct().order_by('year')
dates = []
for item in bal_years:
    dates.append(item['year__year'])


k = itemgetter('member','header','eng_name')
i = groupby(sorted(johns, key=k), key=k)
for key, marks in i:
    indiv_dates = list(dates)
    template = {}
    for mark in marks:
        if itemgetter('year__year')(mark) in indiv_dates:
            indiv_dates.remove(itemgetter('year__year')(mark))
            template = dict(mark)
    if indiv_dates:
        for item in indiv_dates:
            template['year__year'] = item
            template['value'] = ''
            Balances.append(template)
Balances = list(sorted(Balances, key=itemgetter('year__year')))

for Balance in Balances:
    Balance['value'] = Balance.get('value').strip('\n').split(' ',1)[0]

print(Balances)
'''

def year_cleanup(data_set, all_years):

    the_datas = []
    '''
    for item in data_set:
        the_datas.append(item)
    '''

    for item in data_set:
        if item['member'] == '':
            head = item.get('header')
            item['header'] = head.upper()
            the_datas.append(item)


    marks = []
    johns = []
    for item in data_set:
        marks.append(item)
        johns.append(item)
    insert = []

    dates = []
    for item in all_years:
        dates.append(item)

    k = itemgetter('member','header','eng_name')
    i = groupby(sorted(johns, key=k), key=k)
    for key, marks in i:
        #print(key)
        indiv_dates = []
        for date in dates:
            indiv_dates.append(date)
        template = {}
        for mark in marks:
            #print(itemgetter('year__year')(mark))
            if itemgetter('year__year')(mark) in indiv_dates:
                indiv_dates.remove(itemgetter('year__year')(mark))
                template = dict(mark)

        #print(template)
        #print(indiv_dates)
        empty = []
        if indiv_dates:
            for item in indiv_dates:
                smith = dict(template)
                smith['year__year'] = item
                smith['value'] = ''
                the_datas.append(smith)
    for item in the_datas:
        item['value'] = item.get('value').strip('\n').split(' ',1)[0]

    duplic_year = []
    for item in the_datas:
        duplic_year.append(item)

    k = itemgetter('member','header','eng_name', 'year__year')
    i = groupby(sorted(duplic_year, key=k), key=k)
    terminate = []
    for key, marks in i:
        test_len = 0
        report_years = []
        new_marks = []
        for mark in marks:
            print(mark)
            report_years.append(itemgetter('report_period__year')(mark))
            test_len+=1
            new_marks.append(mark)

        #print(new_marks)
        if test_len > 1:
            print(report_years)
            latest_report = max(report_years)
            print('LATEST REPORT YEAR: '+str(latest_report))
            not_term = {}
            for item in new_marks:
                if item.get('report_period__year') == latest_report:
                    not_term = dict(mark)
                    break
            print('NOT TERMINATE')
            print(not_term)
            print('NOT TERMINATE')
            for item in new_marks:
                if item != not_term:
                    terminate.append(item)
            #print(terminate)
    for item in terminate:
        term = item
        for item in duplic_year:
            if item == term:
                duplic_year.remove(item)

    #the_datas = duplic_year


    the_datas = []
    for item in duplic_year:
        if item['member'] == '':
            the_datas.append(item)


    the_datas = sorted(the_datas, key=lambda k: k['year__year'])

    return the_datas



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

#print('ZOO WEE MAMA')
#print(CashFlow.objects.values('year__year').filter(accession_number__in=['0001393612-12-000008', '0001193125-11-014919', '0001393612-16-000059', '0001393612-13-000004', '0001393612-14-000012', '0001393612-15-000007', '0001393612-17-000012', '0001393612-18-000012', '0001393612-19-000011']).distinct())

def home(request):
    context = {
        'Companies': companies,
        'Articles': articles
    }
    return render(request, 'aureum/home.html', context)

def information(request):
    myCountry = request.GET.get('myCountry')
    #if they enter a ticker make sure a name is displayed rather than the ticker
    for item in new_list:
        if item['ticker'] == myCountry or item['name'] == myCountry:
            myCountry = item['name']
    #We've already set mycountry as get. so if get is submitted we dont have to worry about it. just makesure the session is set to the mycountry
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    companyInfo = Company.objects.values('name', 'ticker', 'classification', 'cik').filter(name=myCountry)
    #NOW GET THE CIK AND PREPARE TO FILTER DOWN THE ACCESSION NUMBER
    context = {
        'Company': myCountry,
        'Companies': companies,
        'Informations': companyInfo
    }
    return render(request, 'aureum/information.html', context)

def balance(request):
    myCountry = request.GET.get('myCountry')
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    #GET THE CIK AND CORESSPONDING ACCESSION NUMBERS
    ciks = Company.objects.values('cik').filter(name=myCountry)
    for item in ciks:
        cik = item['cik']
    accessions = Scrape.objects.values('accession_number').filter(cik=cik, filing_type='10-K')
    access = []
    for accession in accessions:
        access.append(accession['accession_number'])
    #Get Max and Min Year
    bal_years =  Balance.objects.values('year__year').filter(accession_number__in=access).distinct().order_by('year')
    new_bal_year = []
    for item in bal_years:
        new_bal_year.append(item['year__year'])
    bal_min = min(new_bal_year)
    bal_max = max(new_bal_year)
    #filter the BALANCE SHEET BASED ON ACCESSION NUMBERS NOW and FILL IN THE BLANKS
    theBalance = Balance.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year__year', 'report_period__year').distinct().filter(accession_number__in=access).order_by('year')
    finBalance = year_cleanup(theBalance, new_bal_year)
    #SEE IF THERE IS YEAR REQUEST
    context = {
        'Datas': finBalance,
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
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    #GET THE CIK AND CORESSPONDING ACCESSION NUMBERS
    ciks = Company.objects.values('cik').filter(name=myCountry)
    for item in ciks:
        cik = item['cik']
    accessions = Scrape.objects.values('accession_number').filter(cik=cik, filing_type='10-K')
    access = []
    for accession in accessions:
        access.append(accession['accession_number'])
    #Get Max and Min Year
    inc_years =  Income.objects.values('year__year').filter(accession_number__in=access).distinct().order_by('year')
    new_inc_year = []
    for item in inc_years:
        new_inc_year.append(item['year__year'])
    inc_min = min(new_inc_year)
    inc_max = max(new_inc_year)
    #filter the BALANCE SHEET BASED ON ACCESSION NUMBERS NOW and FILL IN THE BLANKS
    theIncome = Income.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year__year', 'report_period__year').distinct().filter(accession_number__in=access).order_by('year')
    finIncome = year_cleanup(theIncome, new_inc_year)
    context = {
        'Datas': finIncome,
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
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    if request.GET.get('myCountry') is not None:
        request.session['myCountry'] = myCountry
    else:
        myCountry = request.session['myCountry']
    #GET THE CIK AND CORESSPONDING ACCESSION NUMBERS
    ciks = Company.objects.values('cik').filter(name=myCountry)
    for item in ciks:
        cik = item['cik']
    accessions = Scrape.objects.values('accession_number').filter(cik=cik, filing_type='10-K')
    access = []
    for accession in accessions:
        access.append(accession['accession_number'])
    #Get Max and Min Year
    if year1 is not None:
        cash_years =  CashFlow.objects.values('year__year').filter(accession_number__in=access, year__year__range=(year1, year2)).distinct().order_by('year')
        new_cash_year = []
        for item in cash_years:
            new_cash_year.append(item['year__year'])
        cash_min = min(new_cash_year)
        cash_max = max(new_cash_year)
    else:
        cash_years =  CashFlow.objects.values('year__year').filter(accession_number__in=access).distinct().order_by('year')
        new_cash_year = []
        for item in cash_years:
            new_cash_year.append(item['year__year'])
        cash_min = min(new_cash_year)
        cash_max = max(new_cash_year)
    #filter the BALANCE SHEET BASED ON ACCESSION NUMBERS NOW and FILL IN THE BLANKS
    if year1 is not None:
        theCash = CashFlow.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year__year', 'report_period__year').distinct().filter(accession_number__in=access, year__year__range=(year1, year2)).order_by('year')
        curr_cash_min = year1
        curr_cash_max = year2
    else:
        theCash = CashFlow.objects.values('member', 'header', 'acc_name', 'eng_name','value', 'unit', 'year__year', 'report_period__year').distinct().filter(accession_number__in=access).order_by('year')
        curr_cash_min = cash_min
        curr_cash_max = cash_max
    finCash = year_cleanup(theCash, new_cash_year)
    #RESET THE MIN MAX
    cash_years =  CashFlow.objects.values('year__year').filter(accession_number__in=access).distinct().order_by('year')
    new_cash_year = []
    for item in cash_years:
        new_cash_year.append(item['year__year'])
    cash_min = min(new_cash_year)
    cash_max = max(new_cash_year)
    context = {
        'Datas': finCash,
        'Max': cash_max,
        'Min': cash_min,
        'Curr_Min': curr_cash_min,
        'Curr_Max': curr_cash_max,
        'Company': myCountry,
        'Companies': companies,
        'Statement': 'Cash Flow'
        }
    return render(request, 'aureum/base.html', context)
