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
import requests
from urllib.request import Request, urlopen

# Create your views here.
# Link to actual SEC site https://www.sec.gov/cgi-bin/viewer?action=view&cik=1067983&accession_number=0001193125-10-043450&xbrl_type=v#
#NEWS ARTICLE CATCHING
#def year_cleanup(data_set, all_years):
#    bal_key = itemgetter('member')
#    bal_iter = groupby(sorted(theBalance, key=bal_key), key=bal_key)
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
                        item['value'] = round(float(item['value']), 2)
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
        for item in balances:
            #print(itemgetter('year__year')(mark))
            if itemgetter('year__year')(item) in indiv_dates:
                #if year is accounted delete from indiv_dates
                indiv_dates.remove(itemgetter('year__year')(item))
                template = item.copy()
        #if indiv_dates is not empty, there are unaccounted for years
        if indiv_dates:
            for item in indiv_dates:
                smith = template.copy()
                smith['year__year'] = item
                smith['value'] = '-'
                smith['eng_name'] = 'N/A'
                final_set.append(smith)

    final_set = sorted(final_set, key=lambda k: k['year__year'])

    return final_set

ASSETS = [{'member': 'ASSETS', 'position': 0, 'item': 'Cash And Equivalents'}, {'member': 'ASSETS', 'position': 1, 'item': 'Restricted Cash'}, {'member': 'ASSETS', 'position': 2, 'item': 'Short Term Investments'}, {'member': 'ASSETS', 'position': 3, 'item': 'Trading Asset Securities'}, {'member': 'ASSETS', 'position': 4, 'item': 'Total Cash & ST Investments'}, {'member': 'ASSETS', 'position': 5, 'item': 'Accounts Receivable'}, {'member': 'ASSETS', 'position': 6, 'item': 'Notes Receivable'}, {'member': 'ASSETS', 'position': 7, 'item': 'Other Receivables'}, {'member': 'ASSETS', 'position': 8, 'item': 'Total Receivables'}, {'member': 'ASSETS', 'position': 9, 'item': 'Inventory'}, {'member': 'ASSETS', 'position': 10, 'item': 'Deferred Tax Assets, Curr.'}, {'member': 'ASSETS', 'position': 11, 'item': 'Other Current Assets'}, {'member': 'ASSETS', 'position': 12, 'item': 'Total Current Assets'}, {'member': 'ASSETS', 'position': 13, 'item': 'Gross Property, Plant & Equipment'}, {'member': 'ASSETS', 'position': 14, 'item': 'Accumulated Depreciation'}, {'member': 'ASSETS', 'position': 15, 'item': 'Net Property, Plant & Equipment'}, {'member': 'ASSETS', 'position': 16, 'item': 'Long-term Investments'}, {'member': 'ASSETS', 'position': 17, 'item': 'Goodwill'}, {'member': 'ASSETS', 'position': 18, 'item': 'Other Intangibles'}, {'member': 'ASSETS', 'position': 19, 'item': 'Deferred Tax Assets, LT'}, {'member': 'ASSETS', 'position': 20, 'item': 'Other Long-Term Assets'}, {'member': 'ASSETS', 'position': 21, 'item': 'Total Assets'}]

LIABILITIES = [{'member': 'LIABILITIES', 'position': 0, 'item': 'Accounts Payable'}, {'member': 'LIABILITIES', 'position': 1, 'item': 'Accrued Exp.'}, {'member': 'LIABILITIES', 'position': 2, 'item': 'Short-term Borrowings'}, {'member': 'LIABILITIES', 'position': 3, 'item': 'Curr. Port. of LT Debt'}, {'member': 'LIABILITIES', 'position': 4, 'item': 'Curr. Income Taxes Payable'}, {'member': 'LIABILITIES', 'position': 5, 'item': 'Unearned Revenue, Current'}, {'member': 'LIABILITIES', 'position': 6, 'item': 'Interest Capitalized'}, {'member': 'LIABILITIES', 'position': 7, 'item': 'Other Current Liabilities'}, {'member': 'LIABILITIES', 'position': 8, 'item': 'Total Current Liabilities'}, {'member': 'LIABILITIES', 'position': 9, 'item': 'Long-Term Debt'}, {'member': 'LIABILITIES', 'position': 10, 'item': 'Capital Leases'}, {'member': 'LIABILITIES', 'position': 11, 'item': 'Unearned Revenue, Non-Current'}, {'member': 'LIABILITIES', 'position': 12, 'item': 'Def. Tax Liability, Non-Curr.'}, {'member': 'LIABILITIES', 'position': 13, 'item': 'Other Non-Current Liabilities'}, {'member': 'LIABILITIES', 'position': 14, 'item': 'Total Liabilities'}, {'member': 'LIABILITIES', 'position': 15, 'item': 'Common Stock'}, {'member': 'LIABILITIES', 'position': 16, 'item': 'Additional Paid In Capital'}, {'member': 'LIABILITIES', 'position': 17, 'item': 'Retained Earnings'}, {'member': 'LIABILITIES', 'position': 18, 'item': 'Treasury Stock'}, {'member': 'LIABILITIES', 'position': 19, 'item': 'Comprehensive Inc. and Other'}, {'member': 'LIABILITIES', 'position': 20, 'item': 'Total Common Equity'}, {'member': 'LIABILITIES', 'position': 21, 'item': 'Total Shares Out.'}, {'member': 'LIABILITIES', 'position': 22, 'item': 'Total Equity'}, {'member': 'LIABILITIES', 'position': 23, 'item': 'Total Liabilities And Equity'}]

GENERAL = [{'member': 'GENERAL', 'position': 0, 'item': 'Revenue'}, {'member': 'GENERAL', 'position': 1, 'item': 'Other Revenue'}, {'member': 'GENERAL', 'position': 2, 'item': 'Total Revenue'}, {'member': 'GENERAL', 'position': 3, 'item': 'Cost Of Goods Sold'}, {'member': 'GENERAL', 'position': 4, 'item': 'Gross Profit'}, {'member': 'GENERAL', 'position': 5, 'item': 'Selling General & Admin Exp. '}, {'member': 'GENERAL', 'position': 6, 'item': 'R & D Exp.'}, {'member': 'GENERAL', 'position': 7, 'item': 'Depreciation & Amort.'}, {'member': 'GENERAL', 'position': 8, 'item': 'Other Operating Expense/(Income)'}, {'member': 'GENERAL', 'position': 9, 'item': 'Operating Exp., Total'}, {'member': 'GENERAL', 'position': 10, 'item': 'Operating Income'}, {'member': 'GENERAL', 'position': 11, 'item': 'Interest Expense'}, {'member': 'GENERAL', 'position': 12, 'item': 'Interest and Invest. Income'}, {'member': 'GENERAL', 'position': 13, 'item': 'Net Interest Exp.'}, {'member': 'GENERAL', 'position': 14, 'item': 'Currency Exchange Gains'}, {'member': 'GENERAL', 'position': 15, 'item': 'Other Non-Operating Inc. (Exp.)'}, {'member': 'GENERAL', 'position': 16, 'item': 'EBT Excl. Unusual Items'}, {'member': 'GENERAL', 'position': 17, 'item': 'Restructuring Charges'}, {'member': 'GENERAL', 'position': 18, 'item': 'Merger & Related Restruct. Charges'}, {'member': 'GENERAL', 'position': 19, 'item': 'Impairment of Goodwill'}, {'member': 'GENERAL', 'position': 20, 'item': 'Gain (Loss) On Sale Of Invest.'}, {'member': 'GENERAL', 'position': 21, 'item': 'Asset Writedown'}, {'member': 'GENERAL', 'position': 22, 'item': 'Other Unusual Items'}, {'member': 'GENERAL', 'position': 23, 'item': 'EBT Incl. Unusual Items'}, {'member': 'GENERAL', 'position': 24, 'item': 'Income Tax Expense'}, {'member': 'GENERAL', 'position': 25, 'item': 'Earnings from Cont. Ops.'}, {'member': 'GENERAL', 'position': 26, 'item': 'Earnings of Discontinued Ops.'}, {'member': 'GENERAL', 'position': 27, 'item': 'Other Changes'}, {'member': 'GENERAL', 'position': 28, 'item': 'Net Income to Company'}, {'member': 'GENERAL', 'position': 29, 'item': 'Minority Int. in Earnings'}, {'member': 'GENERAL', 'position': 30, 'item': 'Net Income'}, {'member': 'GENERAL', 'position': 31, 'item': 'Pref. Dividends and Other Adj.'}]

Per_Share_Items = [{'member': 'Per Share Items', 'position': 0, 'item': 'Basic EPS'}, {'member': 'Per Share Items', 'position': 1, 'item': 'Weighted Avg. Basic Shares Out.'}, {'member': 'Per Share Items', 'position': 2, 'item': 'Diluted EPS'}, {'member': 'Per Share Items', 'position': 3, 'item': 'Weighted Avg. Diluted Shares Out.'}]

OPERATING_ACTIVITY = [{'member': 'OPERATING ACTIVITY', 'position': 0, 'item': 'Net Income'}, {'member': 'OPERATING ACTIVITY', 'position': 1, 'item': 'Depreciation & Amort.'}, {'member': 'OPERATING ACTIVITY', 'position': 2, 'item': 'Amort. of Goodwill and Intangibles'}, {'member': 'OPERATING ACTIVITY', 'position': 3, 'item': 'Depreciation & Amort., Total'}, {'member': 'OPERATING ACTIVITY', 'position': 4, 'item': 'Stock-Based Compensation'}, {'member': 'OPERATING ACTIVITY', 'position': 5, 'item': 'Net Cash From Discontinued Ops.'}, {'member': 'OPERATING ACTIVITY', 'position': 6, 'item': 'Other Operating Activities'}, {'member': 'OPERATING ACTIVITY', 'position': 7, 'item': 'Change in Acc. Receivable'}, {'member': 'OPERATING ACTIVITY', 'position': 8, 'item': 'Change In Inventories'}, {'member': 'OPERATING ACTIVITY', 'position': 9, 'item': 'Change in Acc. Payable'}, {'member': 'OPERATING ACTIVITY', 'position': 10, 'item': 'Change in Unearned Rev.'}, {'member': 'OPERATING ACTIVITY', 'position': 11, 'item': 'Cash from Ops.'}]

INVESTING_ACTIVIES = [{'member': 'INVESTING ACTIVIES', 'position': 0, 'item': 'Capital Expenditure'}, {'member': 'INVESTING ACTIVIES', 'position': 1, 'item': 'Cash Acquisitions'}, {'member': 'INVESTING ACTIVIES', 'position': 2, 'item': 'Divestitures'}, {'member': 'INVESTING ACTIVIES', 'position': 3, 'item': 'Purchase of Marketable Equity Securities'}, {'member': 'INVESTING ACTIVIES', 'position': 4, 'item': 'Sale of Marketable Equity Securities'}, {'member': 'INVESTING ACTIVIES', 'position': 5, 'item': 'Net (Inc.) Dec. in Loans Originated/Sold'}, {'member': 'INVESTING ACTIVIES', 'position': 6, 'item': 'Other Investing Activities'}, {'member': 'INVESTING ACTIVIES', 'position': 7, 'item': 'Cash from Investing'}]

FINANCING_ACTIVITIES = [{'member': 'FINANCING ACTIVITIES', 'position': 0, 'item': 'Short Term Debt Issued'}, {'member': 'FINANCING ACTIVITIES', 'position': 1, 'item': 'Long-Term Debt Issued'}, {'member': 'FINANCING ACTIVITIES', 'position': 2, 'item': 'Total Debt Issued'}, {'member': 'FINANCING ACTIVITIES', 'position': 3, 'item': 'Short Term Debt Repaid'}, {'member': 'FINANCING ACTIVITIES', 'position': 4, 'item': 'Long-Term Debt Repaid'}, {'member': 'FINANCING ACTIVITIES', 'position': 5, 'item': 'Total Debt Repaid'}, {'member': 'FINANCING ACTIVITIES', 'position': 6, 'item': 'Repurchase of Common Stock'}, {'member': 'FINANCING ACTIVITIES', 'position': 7, 'item': 'Issuance of Common Stock'}, {'member': 'FINANCING ACTIVITIES', 'position': 8, 'item': 'Common Dividends Paid'}, {'member': 'FINANCING ACTIVITIES', 'position': 9, 'item': 'Total Dividends Paid'}, {'member': 'FINANCING ACTIVITIES', 'position': 10, 'item': 'Special Dividend Paid'}, {'member': 'FINANCING ACTIVITIES', 'position': 11, 'item': 'Other Financing Activities'}, {'member': 'FINANCING ACTIVITIES', 'position': 12, 'item': 'Cash from Financing'}, {'member': 'FINANCING ACTIVITIES', 'position': 13, 'item': 'Foreign Exchange Rate Adj.'}, {'member': 'FINANCING ACTIVITIES', 'position': 14, 'item': 'Net Change in Cash'}]


def sorter(data_set, statement):
    total_count1 = 0
    total_count2 = 0
    copy = []
    if statement == 'balance':
        for item in ASSETS:
            checks = [t for t in data_set if t['standard_name'] == item['item']]
            for check in checks:
                check['member'] = str(item['member'])
                check['member_position'] = 1
                check['position'] = int(item['position'])
                copy.append(check)

        for item in LIABILITIES:
            checks = [t for t in data_set if t['standard_name'] == item['item']]
            for check in checks:
                check['member'] = str(item['member'])
                check['member_position'] = 2
                check['position'] = int(item['position'])
                copy.append(check)

    elif statement == 'income':
        for item in GENERAL:
            checks = [t for t in data_set if t['standard_name'] == item['item']]
            for check in checks:
                check['member'] = str(item['member'])
                check['member_position'] = 1
                check['position'] = int(item['position'])
                copy.append(check)

        for item in Per_Share_Items:
            checks = [t for t in data_set if t['standard_name'] == item['item']]
            for check in checks:
                check['member'] = str(item['member'])
                check['member_position'] = 2
                check['position'] = int(item['position'])
                copy.append(check)

    elif statement == 'cash_flow':
        for item in OPERATING_ACTIVITY:
            checks = [t for t in data_set if t['standard_name'] == item['item']]
            for check in checks:
                check['member'] = str(item['member'])
                check['member_position'] = 1
                check['position'] = int(item['position'])
                copy.append(check)

        for item in INVESTING_ACTIVIES:
            checks = [t for t in data_set if t['standard_name'] == item['item']]
            for check in checks:
                check['member'] = str(item['member'])
                check['member_position'] = 2
                check['position'] = int(item['position'])
                copy.append(check)

        for item in FINANCING_ACTIVITIES:
            checks = [t for t in data_set if t['standard_name'] == item['item']]
            for check in checks:
                check['member'] = str(item['member'])
                check['member_position'] = 3
                check['position'] = int(item['position'])
                copy.append(check)

    for item in copy:
        if '-' not in str(item['value']):
            value = float(item['value'])
            item['value'] = f'{value:,}'
        if '-' in str(item['value']) and str(item['value']) != '-':
            value = float(str(item['value']).strip())
            item['value'] = f'{value:,}'
            item['value'] = '(' + str(item['value']).strip('-') + ')'

    copy = sorted(copy, key=lambda k: k['year__year'])
    return copy
    #elif statement == 'balance':
    #elif statement == 'income':
'''
def company_news(ticker):
    URL="https://finviz.com/quote.ashx?t=%s"%(ticker)
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
        all_news.append(single)
    print(all_news)
    return all_news
'''

#UPDATED NEWS SOURCING
articles = []
urls = ['https://www.bloomberg.com/markets','https://www.wsj.com/news/business','https://www.cnbc.com']
for url in urls:
    if 'bloomberg' in url:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
        soup = BeautifulSoup(page, features="lxml")
        news = soup.find_all("a", {"class": "story-package-module__story__headline-link"})
        for new in news:
            dict = {}
            dict['source'] = 'bloom'
            dict['link'] = 'https://www.bloomberg.com' + str(new['href'])
            dict['title'] = str(new.text).strip()
            articles.append(dict)

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
                if 'cnbc' in url:
                    dict['source'] = 'cnbc'
                elif 'wsj' in url:
                    dict['source'] = 'wsj'
                dict['link'] = link['href']
                dict['title'] = link.text
                articles.append(dict)


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
        'Articles': articles,
    }
    return render(request, 'aureum/home.html', context)

def information(request):
    search = request.GET.get('search')
    #if they enter a ticker make sure a name is displayed rather than the ticker
    for item in new_list:
        if item['ticker'] == search or item['name'] == search:
            ticker = item['ticker']
            search = item['name']
    #We've already set search as get. so if get is submitted we dont have to worry about it. just makesure the session is set to the search
    if request.GET.get('search') is not None:
        request.session['search'] = search
    else:
        search = request.session['search']
    companyInfo = Company.objects.values('name', 'ticker', 'classification_name', 'cik', 'description').filter(name=search)
    #NOW GET THE CIK AND PREPARE TO FILTER DOWN THE ACCESSION NUMBER
    #news = company_news(ticker)
    context = {
        'Company': search,
        'Companies': companies,
        #'News': news,
        'Informations': companyInfo
    }
    return render(request, 'aureum/information.html', context)

def balance(request):
    search = request.GET.get('search')
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    if request.GET.get('search') is not None:
        request.session['search'] = search
    else:
        search = request.session['search']
    #GET THE CIK AND CORESSPONDING ACCESSION NUMBERS
    ciks = Company.objects.values('cik').filter(name=search)
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
    finStatement = sorter(finStatement, 'balance')
    #SEE IF THERE IS YEAR REQUEST
    context = {
        'Datas': finStatement,
        'Max': state_max,
        'Min': state_min,
        'Curr_Max': curr_max,
        'Curr_Min': curr_min,
        'Company': search,
        'Companies': companies,
        'Statement': 'Balance Sheet'
    }
    return render(request, 'aureum/base.html', context)

def income(request):
    search = request.GET.get('search')
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    if request.GET.get('search') is not None:
        request.session['search'] = search
    else:
        search = request.session['search']
    #GET THE CIK AND CORESSPONDING ACCESSION NUMBERS
    ciks = Company.objects.values('cik').filter(name=search)
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
    finStatement = sorter(finStatement, 'income')
    #SEE IF THERE IS YEAR REQUEST
    context = {
        'Datas': finStatement,
        'Max': state_max,
        'Min': state_min,
        'Curr_Max': curr_max,
        'Curr_Min': curr_min,
        'Company': search,
        'Companies': companies,
        'Statement': 'Income Statement'
    }
    return render(request, 'aureum/base.html', context)



def cash(request):
    search = request.GET.get('search')
    year1 = request.GET.get('yearOne')
    year2 = request.GET.get('yearTwo')
    if request.GET.get('search') is not None:
        request.session['search'] = search
    else:
        search = request.session['search']
    #GET THE CIK AND CORESSPONDING ACCESSION NUMBERS
    ciks = Company.objects.values('cik').filter(name=search)
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
    finStatement = sorter(finStatement, 'cash_flow')
    #SEE IF THERE IS YEAR REQUEST
    context = {
        'Datas': finStatement,
        'Max': state_max,
        'Min': state_min,
        'Curr_Max': curr_max,
        'Curr_Min': curr_min,
        'Company': search,
        'Companies': companies,
        'Statement': 'Cash Flow'
        }
    return render(request, 'aureum/base.html', context)


'''
.grid-container {
  border-top: 1px solid #DADCE0;
  overflow-x: hidden;
}


<div class="navbar-header">
<img style = 'margin-right:20px' alt="" src="{% static 'images/Banner.png' %}">
</div>

<head>
  <title>Aureum</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
  <link rel="icon" href="/docs/4.0/assets/img/favicons/favicon.ico">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
  <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
  <script type="text/javascript" src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  <script>
    var companies = {{ Companies|safe }};
  </script>
  <link rel="stylesheet" href='{% static "css/news.css" %}'>
</head>
'''

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





urls = ['https://www.cnbc.com/finance/','https://www.cnn.com/business/investing','https://www.foxbusiness.com/markets']
articles = []
cnn = []
cnbc = []
fox = []
for url in urls:
    if 'cnbc' in url:
        link_head = 'cnbc.com'
        source = 'cnbc'
    elif 'foxbusiness'in url:
        link_head = 'foxbusiness.com'
        source = 'fox'
    elif 'cnn'in url:
        link_head = 'cnn.com'
        source = 'cnn'
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
                art_dict['source'] = source
                articles.append(art_dict)
                if source == 'cnn':
                    cnn.append(art_dict)
                elif source == 'fox':
                    fox.append(art_dict)
                elif source == 'cnbc':
                    cnbc.append(art_dict)
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
                art_dict['source'] = source
                articles.append(art_dict)
                if source == 'cnn':
                    cnn.append(art_dict)
                elif source == 'fox':
                    fox.append(art_dict)
                elif source == 'cnbc':
                    cnbc.append(art_dict)
                i+=1
            else:
                break

'''

'''
<div class="fp-cell fp-cell--1">
    <a class="fp-item" href={{ Articles.0.link }} target="_blank">{{ Articles.0.title }}</a>
</div>
<div class="fp-cell fp-cell--2">
    <a class="fp-item" href={{ Articles.1.link }} target="_blank">{{ Articles.1.title }}</a>
</div>
<div class="fp-cell fp-cell--3">
    <a class="fp-item" href={{ Articles.2.link }} target="_blank">{{ Articles.2.title }}</a>
</div>
<div class="fp-cell fp-cell--4">
  <a class="fp-item" href={{ Articles.3.link }} target="_blank">{{ Articles.3.title }}</a>
</div>
<div class="fp-cell fp-cell--5">
  <a class="fp-item" href={{ Articles.4.link }} target="_blank">{{ Articles.4.title }}</a>
</div>
<div class="fp-cell fp-cell--5">
  <a class="fp-item" href={{ Articles.5.link }} target="_blank">{{ Articles.5.title }}</a>
</div>
<div class="fp-hold fp-cell--6 sticky">
  <h4 style='text-align: center;'>Indeces</h4>
</div>
{% for Article in Articles %}
  {% if Article.title != Articles.5.title %}
    {% if Article.title != Articles.4.title %}
      {% if Article.title != Articles.3.title %}
        {% if Article.title != Articles.2.title %}
          {% if Article.title != Articles.1.title %}
            {% if Article.title != Articles.0.title %}
              <div class="fp-cell fp-cell--7"> <a class="fp-item" href={{ Article.link }} target="_blank">{{ Article.title }}</a> </div>
            {% endif %}
          {% endif %}
        {% endif %}
      {% endif %}
    {% endif %}
  {% endif %}
{% endfor %}
{% for New in News %}
  <p>{{ New.title }}</p>
{% endfor %}
'''
