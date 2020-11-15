from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Prefetch
from .models import Balance, CashFlow, Income, NonStatement, Company, Scrape, StandardIncome, StandardCash, StandardBalance
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
#balances = StandardBalance.objects.values('header', 'standard_name', 'eng_name', 'acc_name', 'value', 'unit', 'year', 'statement', 'report_period', 'filing_type', 'accession_number').filter(accession_number__in=['0000320193-17-000070','0001628280-16-020309','0001193125-15-356351']).distinct()
#print(Balances)
def standardization(data_set, min_year, max_year):
    balances = []
    for item in data_set:
        balances.append(item)
    k = itemgetter('standard_name','year__year')
    #get the one with most recent report year and year
    final_list = []
    i = groupby(sorted(balances, key=k), key=k)
    for key, balances in i:
        #print(key)
        report_years = []
        bal_2 = []
        for balance in balances:
            report_years.append(balance['report_period'])
            bal_2.append(balance)
        latest_report = max(report_years)
        #got the most recent report year now put the most recent releveant stuff into there
        done = False
        for item in bal_2:
            if done == False:
                if str(item['report_period']) == str(latest_report):
                    if int(min_year) <= item['year__year'] <= int(max_year):
                        #print(item['report_period'], item['value'], item['accession_number'])
                        final_list.append(item)
                        done = True
    return final_list
#for item in final_list:
#    print(item['standard_name'], item['year'], item['value'])
    #get most recent year from filered list

    #get most recent date

#Stand_Stat = StandardIncome.objects.values().filter(accession_number = "0001193125-11-014919")
#print(Stand_Stat)


#THIS FUNCTION FILLS IN MISSING YEARS
def year_cleanup(data_set, all_years):
    final_set = []
    balances = []
    dates = []
    #duplicate data
    for item in data_set:
        balances.append(item)
        final_set.append(item)
        print(item)

    for item in all_years:
        dates.append(item)
    k = itemgetter('standard_name')
    #get the one with most recent report year and year
    i = groupby(sorted(balances, key=k), key=k)
    for key, balances in i:
        year_list = []
        indiv_dates = []
        #create new list for all dates
        for date in dates:
            indiv_dates.append(date)
        template = {}
        #check if the years are accounted for
        for balance in balances:
            #print(itemgetter('year__year')(mark))
            if itemgetter('year__year')(balance) in indiv_dates:
                #if year is accounted delete from indiv_dates
                indiv_dates.remove(itemgetter('year__year')(balance))
                template = dict(balance)
        #if indiv_dates is not empty, there are unaccounted for years
        if indiv_dates:
            for item in indiv_dates:
                smith = dict(template)
                smith['year__year'] = item
                smith['value'] = '-'
                print(smith)
                final_set.append(smith)

    final_set = sorted(final_set, key=lambda k: k['year__year'])

    return final_set



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
    state_years = StandardBalance.objects.values('year__year').filter(accession_number__in=access).distinct().order_by('year__year')
    #see what the displayed curr min max is
    new_state_year = []
    for item in state_years:
        new_state_year.append(item['year__year'])
    state_min = min(new_state_year)
    state_max = max(new_state_year)
    if year1 is not None:
        curr_min = year1
        curr_max = year2
        newest = []
        for item in new_state_year:
            if int(curr_min) <= int(item) <= int(curr_max):
                newest.append(item)
        new_state_year = newest
    else:
        curr_min = min(new_state_year)
        curr_max = max(new_state_year)
    #filter the BALANCE SHEET BASED ON ACCESSION NUMBERS NOW and FILL IN THE BLANKS
    theStatement = StandardBalance.objects.values('header', 'standard_name', 'eng_name', 'acc_name', 'value', 'unit', 'year__year', 'statement', 'report_period', 'filing_type', 'accession_number').filter(accession_number__in = access).distinct()
    finStatement = standardization(theStatement, curr_min, curr_max)
    finStatement = year_cleanup(finStatement, new_state_year)
    #SEE IF THERE IS YEAR REQUEST
    context = {
        'Datas': finStatement,
        'Max': state_max,
        'Min': state_min,
        'Curr_Max': curr_max,
        'Curr_Min': curr_min,
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
    state_years = StandardIncome.objects.values('year__year').filter(accession_number__in=access).distinct().order_by('year__year')
    #see what the displayed curr min max is
    new_state_year = []
    for item in state_years:
        new_state_year.append(item['year__year'])
    state_min = min(new_state_year)
    state_max = max(new_state_year)
    if year1 is not None:
        curr_min = year1
        curr_max = year2
        newest = []
        for item in new_state_year:
            if int(curr_min) <= int(item) <= int(curr_max):
                newest.append(item)
        new_state_year = newest
    else:
        curr_min = min(new_state_year)
        curr_max = max(new_state_year)
    #filter the BALANCE SHEET BASED ON ACCESSION NUMBERS NOW and FILL IN THE BLANKS
    theStatement = StandardIncome.objects.values('header', 'standard_name', 'eng_name', 'acc_name', 'value', 'unit', 'year__year', 'statement', 'report_period', 'filing_type', 'accession_number').filter(accession_number__in = access).distinct()
    finStatement = standardization(theStatement, curr_min, curr_max)
    finStatement = year_cleanup(finStatement, new_state_year)
    #SEE IF THERE IS YEAR REQUEST
    context = {
        'Datas': finStatement,
        'Max': state_max,
        'Min': state_min,
        'Curr_Max': curr_max,
        'Curr_Min': curr_min,
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
    state_years = StandardCash.objects.values('year__year').filter(accession_number__in=access).distinct().order_by('year__year')
    #see what the displayed curr min max is
    new_state_year = []
    for item in state_years:
        new_state_year.append(item['year__year'])
    state_min = min(new_state_year)
    state_max = max(new_state_year)
    if year1 is not None:
        curr_min = year1
        curr_max = year2
        newest = []
        for item in new_state_year:
            if int(curr_min) <= int(item) <= int(curr_max):
                newest.append(item)
        new_state_year = newest
    else:
        curr_min = min(new_state_year)
        curr_max = max(new_state_year)
    #filter the BALANCE SHEET BASED ON ACCESSION NUMBERS NOW and FILL IN THE BLANKS
    theStatement = StandardCash.objects.values('header', 'standard_name', 'eng_name', 'acc_name', 'value', 'unit', 'year__year', 'statement', 'report_period', 'filing_type', 'accession_number').filter(accession_number__in = access).distinct()
    finStatement = standardization(theStatement, curr_min, curr_max)
    finStatement = year_cleanup(finStatement, new_state_year)
    #SEE IF THERE IS YEAR REQUEST
    context = {
        'Datas': finStatement,
        'Max': state_max,
        'Min': state_min,
        'Curr_Max': curr_max,
        'Curr_Min': curr_min,
        'Company': myCountry,
        'Companies': companies,
        'Statement': 'Cash Flow'
        }
    return render(request, 'aureum/base.html', context)
