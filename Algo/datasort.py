

#BALANCE SHEET
ASSETS = ['Cash And Equivalents',
'Restricted Cash',
'Short Term Investments',
'Trading Asset Securities',
'Total Cash & ST Investments',
'Accounts Receivable',
'Notes Receivable',
'Other Receivables',
'Total Receivables',
'Inventory',
'Deferred Tax Assets, Curr.',
'Other Current Assets',
'Total Current Assets',
'Gross Property, Plant & Equipment',
'Accumulated Depreciation',
'Net Property, Plant & Equipment',
'Long-term Investments',
'Goodwill',
'Other Intangibles',
'Deferred Tax Assets, LT',
'Other Long-Term Assets',
'Total Assets']



LIABILITIES = ['Accounts Payable',
'Accrued Exp.',
'Short-term Borrowings',
'Curr. Port. of LT Debt',
'Curr. Income Taxes Payable',
'Unearned Revenue, Current',
'Interest Capitalized',
'Other Current Liabilities',
'Total Current Liabilities',
'Long-Term Debt',
'Capital Leases',
'Unearned Revenue, Non-Current',
'Def. Tax Liability, Non-Curr.',
'Other Non-Current Liabilities',
'Total Liabilities',
'Common Stock',
'Additional Paid In Capital',
'Retained Earnings',
'Treasury Stock',
'Comprehensive Inc. and Other',
'Total Common Equity',
'Total Shares Out.',
'Total Equity',
'Total Liabilities And Equity']

#INCOME STATEMENT
GENERAL = [
'Revenue',
'Other Revenue',
'Total Revenue',
'Cost Of Goods Sold',
'Gross Profit',
'Selling General & Admin Exp. ',
'R & D Exp.',
'Depreciation & Amort.',
'Other Operating Expense/(Income)',
'Operating Exp., Total',
'Operating Income',
'Interest Expense',
'Interest and Invest. Income',
'Net Interest Exp.',
'Currency Exchange Gains',
'Other Non-Operating Inc. (Exp.)',
'EBT Excl. Unusual Items',
'Restructuring Charges',
'Merger & Related Restruct. Charges',
'Impairment of Goodwill',
'Gain (Loss) On Sale Of Invest.',
'Asset Writedown',
'Other Unusual Items',
'EBT Incl. Unusual Items',
'Income Tax Expense',
'Earnings from Cont. Ops.',
'Earnings of Discontinued Ops.',
'Other Changes',
'Net Income to Company',
'Minority Int. in Earnings',
'Net Income',
'Pref. Dividends and Other Adj.']




Per_Share_Items = [
'Basic EPS',
'Weighted Avg. Basic Shares Out.',
'Diluted EPS',
'Weighted Avg. Diluted Shares Out.']

#CASH FLOW

OPERATING_ACTIVITY = [
'Net Income',
'Depreciation & Amort.',
'Amort. of Goodwill and Intangibles',
'Depreciation & Amort., Total',
'Stock-Based Compensation',
'Net Cash From Discontinued Ops.',
'Other Operating Activities',
'Change in Acc. Receivable',
'Change In Inventories',
'Change in Acc. Payable',
'Change in Unearned Rev.',
'Cash from Ops.']

INVESTING_ACTIVIES = [
'Capital Expenditure',
'Cash Acquisitions',
'Divestitures',
'Purchase of Marketable Equity Securities',
'Sale of Marketable Equity Securities',
'Net (Inc.) Dec. in Loans Originated/Sold',
'Other Investing Activities',
'Cash from Investing']

FINANCING_ACTIVITIES = [
'Short Term Debt Issued',
'Long-Term Debt Issued',
'Total Debt Issued',
'Short Term Debt Repaid',
'Long-Term Debt Repaid',
'Total Debt Repaid',
'Repurchase of Common Stock',
'Issuance of Common Stock',
'Common Dividends Paid',
'Total Dividends Paid',
'Special Dividend Paid',
'Other Financing Activities',
'Cash from Financing',
'Foreign Exchange Rate Adj.',
'Net Change in Cash']

final_output = []
count = 0
#for item in ASSETS:
#for item in LIABILITIES:
#for item in GENERAL:
#for item in Per_Share_Items:
#for item in FINANCING_ACTIVITIES:
#for item in OPERATING_ACTIVITY:
for item in INVESTING_ACTIVIES:
    dict = {}
    dict['member'] = 'INVESTING ACTIVIES'
    dict['position'] = count
    dict['item'] = item
    final_output.append(dict)
    count+=1

print(final_output)
