complete = False
unfinished = []
years = ['row1', 'row2', 'row3']
while complete == False:
    for item in years:
        if item['status'] == 'pending':
            unfinished.append(item)
    if not unfinished:
        for item in unfinished:
            item.interParse
            #after parsing see if these things are completed if not then keep as pending, if it did complete parse change status to complete
    else:
        break
