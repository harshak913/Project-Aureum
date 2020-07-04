import re
import csv
import requests
import datetime
from dateutil.parser import parse
import unicodedata
import unidecode
import mysql.connector as mariadb
from calendar import month_name
from bs4 import BeautifulSoup

#Pull tables after td, h1, div, or p tags that contain certain title variations of financial statements
def pull_tables(td_tags, h1_tags, div_tags, p_tags, variations_list, table_filename, content_variations):
    title_tag = ''
    sheet = ''
    table_list = []

    #Get text from lists containing tags of title variations
    td_text = get_text_lists(td_tags)
    h1_text = get_text_lists(h1_tags)
    div_text = get_text_lists(div_tags)
    p_text = get_text_lists(p_tags)

    #Check each tag list to find match between variation and text & append that tag to a list
    for a in range(len(td_text)-1):
        for b in variations_list:
            if b.upper() in td_text[a].upper():
                title_tag = td_tags[a]
                sheet = title_tag.find_previous('table')
                table_list.append(sheet)

    for c in range(len(h1_text)-1):
        for d in variations_list:
            if d.upper() in h1_text[c].upper():
                title_tag = h1_tags[c]
                sheet = title_tag.find_next('table')
                table_list.append(sheet)

    for e in range(len(div_text)-1):
        for f in variations_list:
            if f.upper() in div_text[e].upper():
                title_tag = div_tags[e]
                sheet = title_tag.find_next('table')
                table_list.append(sheet)

    for g in range(len(p_text)-1):
        for h in variations_list:
            if h.upper() in p_text[g].upper():
                title_tag = p_tags[g]
                sheet = title_tag.find_next('table')
                table_list.append(sheet)
    return table_list

#Get the text, strip whitespace, split among spaces and join them back to get a proper, normalized string list
def get_text_lists(tags):
    text_list = []
    for i in range(len(tags)):
        split_text = tags[i].get_text().strip().split()
        text_list.append(' '.join(split_text))
    return text_list

#Check each table for row name variations & append to new list if table contains certain number of variations
def check_variations(table_list, table_filename, content_variations):
    new_table_list = []
    if 'balance_sheet' in table_filename:
        for x in range(len(table_list)):
            if table_list[x] is not None:
                if is_balance(table_list[x], content_variations) == True:
                    new_table_list.append(table_list[x])
                else:
                    continue
    elif 'income_statement' in table_filename:
        for y in range(len(table_list)):
            if table_list[y] is not None:
                if is_income(table_list[y], content_variations) == True:
                    new_table_list.append(table_list[y])
                else:
                    continue
    elif 'cash_flows' in table_filename:
        for z in range(len(table_list)):
            if table_list[z] is not None:
                if is_cash_flows(table_list[z], content_variations) == True:
                    new_table_list.append(table_list[z])
                else:
                    continue
    return new_table_list

#Check balance sheet table for row name variations & return True if table contains 3+ variations
def is_balance(specified_table_tag, content_variations):
    variation_count = 0
    for tr_tag in specified_table_tag.find_all('tr'):
        if len(tr_tag.find_all('th')) != 0:
            for th_tag in tr_tag.find_all('th'):
                for variation in content_variations:
                    if variation.upper() in get_fixed_tag_text(th_tag).upper():
                        variation_count += 1
        for td_tag in tr_tag.find_all('td'):
            for variation in content_variations:
                if variation.upper() in get_fixed_tag_text(td_tag).upper():
                    variation_count += 1
    if variation_count >= 3:
        return True
    else:
        return False

#Check income statement table for row name variations & return True if table contains 10+ variations
def is_income(specified_table_tag, content_variations):
    variation_count = 0
    for tr_tag in specified_table_tag.find_all('tr'):
        if len(tr_tag.find_all('th')) != 0:
            for th_tag in tr_tag.find_all('th'):
                for key, value in content_variations.items():
                    for variation in value:
                        if variation.upper() in get_fixed_tag_text(th_tag).upper():
                            variation_count += 1
        for td_tag in tr_tag.find_all('td'):
            for key, value in content_variations.items():
                for variation in value:
                    if variation.upper() in get_fixed_tag_text(td_tag).upper():
                        variation_count += 1
    if variation_count >= 10:
        return True
    else:
        return False

#Check cash flows table for row name variations & return True if table contains 2+ variations
def is_cash_flows(specified_table_tag, content_variations):
    variation_count = 0
    #Check if Index to Consolidated Financial Statements is contained in table (Only appears for cash flows)
    if 'INDEX' in get_fixed_tag_text(specified_table_tag).upper():
        return False
    elif ('INVESTING' in get_fixed_tag_text(specified_table_tag).upper()) or ('OPERATING' in get_fixed_tag_text(specified_table_tag).upper() or 'OPERATION' in get_fixed_tag_text(specified_table_tag).upper()) or ('FINANCING' in get_fixed_tag_text(specified_table_tag).upper()):
        variation_count += 1
    else:
        return False
    for tr_tag in specified_table_tag.find_all('tr'):
        if len(tr_tag.find_all('th')) != 0:
            for th_tag in tr_tag.find_all('th'):
                for variation in content_variations:
                    if variation_count >= 2:
                        break
                    elif variation.upper() in get_fixed_tag_text(th_tag).upper():
                        variation_count += 1
        for td_tag in tr_tag.find_all('td'):
            for variation in content_variations:
                if variation_count >= 2:
                    break
                elif variation.upper() in get_fixed_tag_text(td_tag).upper():
                    variation_count += 1
    if variation_count >= 2:
        return True
    else:
        return False

#Get the text, strip whitespace, split among spaces and join them back to get a proper, normalized string
def get_fixed_tag_text(tag_name):
    return ' '.join(tag_name.get_text().strip().split())


def find_value(in_thousands_lower, in_millions_lower, in_thousands_upper, in_millions_upper, final_list):
    value_list = []
    for item in final_list:
        if 'thousands' in ' '.join(item.get_text().strip().lower().split()):
            value_list.append('In thousands')
    if len(value_list) != 0:
        return value_list
    elif 'millions' in ' '.join(item.get_text().strip().lower().split()):
            value_list.append('In millions')
    if len(value_list) != 0:
        return value_list

    for thousands in in_thousands_lower:
        for item in final_list:
            if thousands.find_next('table') == item:
                value_list.append('In thousands')

    for millions in in_millions_lower:
        for item in final_list:
            if millions.find_next('table') == item:
                value_list.append('In millions')

    for thousands in in_thousands_upper:
        for item in final_list:
            if thousands.find_next('table') == item:
                value_list.append('In thousands')

    for millions in in_millions_upper:
        for item in final_list:
            if millions.find_next('table') == item:
                value_list.append('In millions')
    return value_list

def restore_windows_1252_characters(restore_string):
    def to_windows_1252(match):
        try:
            return bytes([ord(match.group(0))]).decode('cp1252')
        except UnicodeDecodeError:
            # No character at the corresponding code point: remove it.
            return ''
    return re.sub(r'[\u0080-\u0099]', to_windows_1252, restore_string)

#Parses HTML tables and puts them in a CSV format
def parse_tables(in_thousands_lower, in_millions_lower, in_thousands_upper, in_millions_upper, final_list, table_filename):
    value_list = find_value(in_thousands_lower, in_millions_lower, in_thousands_upper, in_millions_upper, final_list)
    years = list(range(2000, datetime.datetime.today().year+1))
    year_pattern = ''
    for year in range(len(years)):
        if year == 0:
            year_pattern = year_pattern + str(years[year])
        else:
            year_pattern = year_pattern + '|' + str(years[year])
    month_pattern = '|'.join(month_name[1:])
    month_abbrev = 'Jan|Feb|Mar|Apr|May|June|July|Aug|Sept|Oct|Nov|Dec'
    month_list = []
    year_list = []
    row_list = []
    header_list = []
    table_count = -1
    header_added = False
    for table in final_list:
        table_count += 1
        for tr in table.find_all('tr'):
            if tr.get_text().strip() != '' and 'in millions' not in tr.get_text().strip().lower():
                if re.search(month_pattern, tr.get_text().strip(), re.IGNORECASE) is not None or re.search(year_pattern, tr.get_text().strip(), re.IGNORECASE) is not None or re.search(month_abbrev, tr.get_text().strip(), re.IGNORECASE) is not None:
                    for td in tr.find_all('td'):
                        if re.search(month_pattern, td.get_text().strip(), re.IGNORECASE) is not None or re.search(month_abbrev, td.get_text().strip(), re.IGNORECASE) is not None:
                            month_list.append(td.get_text().strip())
                        elif td.get_text().strip().isdigit():
                            year_list.append(td.get_text().strip())
                else:
                    with open(table_filename, 'a+', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        if header_added == False:
                            header_list.append('Title')
                            if len(year_list) == 0:
                                for item in month_list:
                                    header_list.append(item)
                            elif len(month_list) == len(year_list):
                                for item in range(len(month_list)):
                                    header_list.append(month_list[item] + ' ' + year_list[item])
                            elif len(month_list) == 1 and len(year_list) > 1:
                                for item in year_list:
                                    header_list.append(month_list[0] + ' ' + item)
                            elif len(month_list) == 0:
                                for item in year_list:
                                    header_list.append(item)
                            header_added = True
                            header_list.append('Value')
                            for row in range(len(header_list)-1):
                                if row >= 1 and row < len(header_list)-1:
                                    cell_list = header_list[row].split()
                                    for cell in range(len(cell_list)):
                                        if re.search(month_pattern, cell_list[cell], re.IGNORECASE) is not None:
                                            header_list[row] = cell_list[cell] + ' ' + cell_list[cell+1] + ' ' + cell_list[cell+2]
                                            break
                            writer.writerow(header_list)
                            month_list.clear()
                            year_list.clear()
                        else:
                            td_table = tr.find_all('td')
                            for td in range(len(td_table)):
                                td_text = unidecode.unidecode(restore_windows_1252_characters(unicodedata.normalize('NFKD', td_table[td].get_text().strip())))
                                if td_text == '$' or td_text == ')' or td_text == '':
                                    continue
                                elif '(' in td_text:
                                    openparen_list = td_text.split('(')
                                    if ')' in openparen_list[1]:
                                        openparen_list[1] = openparen_list[1].strip(')')
                                    if ',' in openparen_list[1]:
                                        comma_list = openparen_list[1].strip().split(',')
                                        num_excl_comma = ''
                                        for comma in comma_list:
                                            num_excl_comma = num_excl_comma + '' + comma
                                        if num_excl_comma.isdigit():
                                            row_list.append('(' + num_excl_comma + ')')
                                    elif openparen_list[1].isdigit() or '.' in openparen_list[1]:
                                        row_list.append('(' + openparen_list[1] + ')')
                                    else:
                                        row_list.append(td_text)
                                else:
                                    row_list.append(td_text)
                            if len(row_list) == 1:
                                for item in range(len(header_list)-2):
                                    row_list.append('')
                            if len(row_list) > 1 and len(value_list) >= 1:
                                row_list.append(value_list[table_count])
                            elif len(value_list) == 0:
                                row_list.append('')
                            if len(row_list) == len(header_list)-1:
                                row_list.insert(0, 'Total')
                            row_list_text_split = row_list[0].split()
                            row_list[0] = row_list_text_split[0]
                            for text in row_list_text_split[1:]:
                                if text == '' or text == '\n':
                                    continue
                                row_list[0] = row_list[0] + ' ' + text
                            writer.writerow(row_list)
                            row_list.clear()

balance_sheet_variations = ['Statement of Net Assets', 'Statements of Net Assets', 'Statement of Financial Position', 'Statements of Financial Position', 'Balance Sheet'] #Balance sheet title variations
balance_sheet_content_variations = ['Current assets', 'Current liabilities', 'Total liabilities', 'Total assets', 'Stockholders\' equity', 'Shareholders\' equity',
                                    'Stockholders\' investment', 'Shareholders\' investment', 'Total investment', 'Total equity', 'Shareholder/stockholders\' equity', 'Accounts payable', 'Accounts receivable',
                                    'Liabilities and Stockholders\' Equity'] #Balance sheet row name variations

income_statement_variations = ['Statement of Earnings', 'Statements of Earnings', 'Statement of Operations', 'Statements of Operations', 'Statement of Income', 'Statements of Income', 'Income Statement'] #Income statement title variations
income_statement_content_variations = {}
income_statement_content_variations['Revenue'] = ['Sales, net', 'Earning', 'Net sale', 'Revenue', 'Net income', 'Net loss']
income_statement_content_variations['Costs/Expenses'] = ['Cost & expenses', 'Cost and expenses', 'Costs & expenses', 'Costs and expenses', 'Cost of product', 'Cost of good', 'Cost of sale', 'Cost of revenue']
income_statement_content_variations['Operating Profit/Expenses'] = ['Total operating', 'Operating cost', 'Operating profit', 'Operating income', 'Gross profit', 'Total expense', 'Operating expense']
income_statement_content_variations['Misc'] = ['Interest expense', 'Administrative', 'Income tax expense', 'Operating income', 'Gross margin', 'Gross profit', 'Research and development', 'Research & development', 'Basic', 'Diluted'] #Income statement row name variations

cash_flows_variations = ['Statement of Cash Flows', 'Statements of Cash Flows', 'Cash Flows Statement'] #Cash flows title variations
cash_flows_content_variations = ['Cash and cash equivalents', 'Cash & cash equivalents', 'Cash and cash', 'Cash & cash', 'Cash & equivalents', 'Cash'] #Cash flows row name variations

def HTMLParse(html_text_filing, strip_htm):
    #html_text_filing = r"https://www.sec.gov/Archives/edgar/data/59558/000136231009002975/0001362310-09-002975.txt"
    #html_text_filing = r"https://www.sec.gov/Archives/edgar/data/46080/000004608002000011/0000046080-02-000011.txt"
    #html_text_filing = r"https://www.sec.gov/Archives/edgar/data/1067983/000095013408003848/0000950134-08-003848.txt"

    response = requests.get(html_text_filing)
    parser = BeautifulSoup(response.content, 'lxml')

    td_tags = parser.select('td')
    h1_tags = parser.select('h1')
    div_tags = parser.select('div')
    p_tags = parser.select('p')

    in_thousands_lower = parser.find_all(text=re.compile('thousands'))
    in_thousands_upper = parser.find_all(text=re.compile('Thousands'))
    in_millions_lower = parser.find_all(text=re.compile('millions'))
    in_millions_upper = parser.find_all(text=re.compile('Millions'))

    #Create balance sheet, income statement, and cash flows files
    balance_sheet_file = '%s-balance_sheet.csv' % (strip_htm)
    income_statement_file = '%s-income_statement.csv' % (strip_htm)
    cash_flows_file = '%s-cash_flows.csv' % (strip_htm)

    balance_sheet_list = pull_tables(td_tags, h1_tags, div_tags, p_tags, balance_sheet_variations, balance_sheet_file, balance_sheet_content_variations)
    balance_sheet_file_list = check_variations(balance_sheet_list, balance_sheet_file, balance_sheet_content_variations)

    income_statement_list = pull_tables(td_tags, h1_tags, div_tags, p_tags, income_statement_variations, income_statement_file, income_statement_content_variations)
    income_statement_file_list = check_variations(income_statement_list, income_statement_file, income_statement_content_variations)

    cash_flows_list = pull_tables(td_tags, h1_tags, div_tags, p_tags, cash_flows_variations, cash_flows_file, cash_flows_content_variations)
    cash_flows_file_list = check_variations(cash_flows_list, cash_flows_file, cash_flows_content_variations)

    # Narrow down to only the appropriate tables
    complete_temp_table_list = parser.select('table')

    #Remove tables with 'PAGE', page numbers, or empty non-breaking spaces
    complete_table_list = []
    for t in range(len(complete_temp_table_list)):
        uniString = complete_temp_table_list[t].get_text()
        if not('PAGE' in uniString.upper()) and not(uniString.isdigit() == True) and not(uniString.strip() == ''):
            complete_table_list.append(complete_temp_table_list[t])

    final_balance_list = []
    final_income_list = []
    final_cash_flows_list = []

    balance_complete_index = 0
    found_balance = False
    for m in range(len(complete_table_list)-1):
        for n in range(len(balance_sheet_file_list)):
            if complete_table_list[m] == balance_sheet_file_list[n]: #If table matches one of the balance sheet tables
                previous_table = complete_table_list[m-1] #Grab previous table
                next_table = complete_table_list[m+1] #Grab next table
                for o in income_statement_file_list:
                    if previous_table == o or next_table == o or is_balance(next_table, balance_sheet_content_variations): #Validates proper balance sheet by checking all variations in table order
                        final_balance_list.append(balance_sheet_file_list[n]) #Append validated balance sheet to final balance sheet table
                        del balance_sheet_file_list[n] #Delete balance sheet table from original list
                        balance_complete_index = m
                        found_balance = True
                        break
            if found_balance == True:
                break
        if found_balance == True: #Break out of entire loop if balance sheet has been found
            break

    complete_index = balance_complete_index
    cash_flows_index = 0
    next_is_income = False
    while complete_index < len(complete_table_list)-1:
        previous_table = complete_table_list[complete_index-1] #Grab previous table
        next_table = complete_table_list[complete_index+1] #Grab next table
        for p in income_statement_file_list:
            if previous_table == p: #If previous table is income, add it to final income list and delete from original list
                final_income_list.append(p)
                income_statement_file_list.remove(p)
                break
            elif next_table == p: #If next table is income, add it to final income list and delete from original list
                final_income_list.append(p)
                income_statement_file_list.remove(p)
                next_is_income = True #Set next income flag to True because if income is next, then balance sheet CANNOT be next
                complete_index += 1
                break
        if next_is_income != True: #Only executes is the next table is not an income statement (ONLY in cases where balance sheet might be split into 2 tables)
            for q in balance_sheet_file_list:
                if next_table == q:
                    final_balance_list.append(q)
                    balance_sheet_file_list.remove(q)
                    complete_index += 1
                    break
        cash_flows_index = complete_index #Sets cash flows index to last table we traversed (income statement or balance sheet)
        if is_cash_flows(next_table, cash_flows_content_variations) == True:
            break
        elif is_balance(next_table, balance_sheet_content_variations) == False and is_income(next_table, income_statement_content_variations) == False:
            break

    complete_index = cash_flows_index
    while complete_index < len(complete_table_list)-1:
        next_table = complete_table_list[complete_index+1] #Grab next table
        for r in cash_flows_file_list:
            if next_table == r: #If next table is a cash flow, add it to final cash flows list and delete from original list
                final_cash_flows_list.append(r)
                cash_flows_file_list.remove(r)
                break
        complete_index += 1
        if complete_index - cash_flows_index >= 3 and is_cash_flows(next_table, cash_flows_content_variations) == False:
            break

    #Write final balance sheet, income statement, and cash flows tables to files
    if len(final_balance_list) != 0:
        parse_tables(in_thousands_lower, in_millions_lower, in_thousands_upper, in_millions_upper, final_balance_list, balance_sheet_file)
    else:
        print("No balance sheets found")
    
    if len(final_income_list) != 0:
        parse_tables(in_thousands_lower, in_millions_lower, in_thousands_upper, in_millions_upper, final_income_list, income_statement_file)
    else:
        print("No income statements found")
    
    if len(final_cash_flows_list) != 0:
        parse_tables(in_thousands_lower, in_millions_lower, in_thousands_upper, in_millions_upper, final_cash_flows_list, cash_flows_file)
    else:
        print("No cash flows statements found")


    """     insert_list = []
        insert_list.append(balance_sheet_file)
        insert_list.append(income_statement_file)
        insert_list.append(cash_flows_file)

        all_dict = []
        for item in insert_list:
            if 'balance' in item:
                statement_insert = 'balance'
                statement = 'Balance Sheet'
            elif 'income' in item:
                statement_insert = 'income'
                statement = 'Income Statement'
            elif 'cash' in item:
                statement_insert = 'cash_flow'
                statement = 'Cash Flow Statement'

            csvfile = open(item, 'r')
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            keys = list(reader.fieldnames)
            for key in keys:
                if key == 'Title':
                    keys.remove(key)
                if key == 'Value':
                    keys.remove(key)

            member = ''
            header = ''
            for row in rows:
                if row['Title'] != 'Title' and row['Value'] != 'Value':
                    i = 0
                    for key in keys:
                        if row[key]:
                            i+=1
                    if i == 0:
                        next = rows[rows.index(row)+1]
                        for key in keys:
                            if next[key]:
                                i+=1
                        if i == 0:
                            member = row['Title']
                        else:
                            header = row['Title']
                    else:
                        for key in keys:
                            dict = {}
                            dict['member'] = member
                            dict['header'] = header
                            dict['eng_name'] = row['Title']
                            dict['value'] = row[key]
                            dict['year'] = key
                            if str(row['Value']).strip() == '':
                                dict['unit'] = 'As Displayed'
                            else:
                                dict['unit'] = row['Value']
                            dict['statement'] = statement
                            dict['insert'] = statement_insert
                            all_dict.append(dict)


        seen = set()
        new_l = []
        for d in all_dict:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)

        for item in new_l:
            connection = mariadb.connect(host="localhost",user="root",passwd="DB^oo^ec@^h@ckth!$0913",database="database",autocommit=True)
            cursor = connection.cursor()
            member = item['member']
            header = item['header']
            eng_name = item['eng_name']
            value = item['value']
            if ',' not in item['year']:
                year = '1-1-'+item['year']
                year = parse(year)
                year = year.date()
            else:
                year = item['year']
                year = parse(year)
                year = year.date()
            unit = item['unit']
            statement = item['statement']
            statement_insert = item['insert']"""

HTMLParse("https://www.sec.gov/Archives/edgar/data/26172/000002617202000002/0000026172-02-000002.txt", "form10k")
# UPDATE parse_tables method so that it removes '$' and '=' from the CSV output (edit row_list before writerow)