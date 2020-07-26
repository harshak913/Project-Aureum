complete = False
unfinished = []
years = ['row1', 'row2', 'row3']
while complete == False:
    for item in years:
        if item['status'] == 'pending':
            unfinished.append(item)
<<<<<<< HEAD
    for item in unfinished:
        item.interParse
    for item in unfinished:
        if sta
        
=======
    if not unfinished:
        for item in unfinished:
            item.interParse
            #after parsing see if these things are completed if not then keep as pending, if it did complete parse change status to complete
    else:
        break
>>>>>>> 38823bcbcf83bf56461d8e1a0111e414092c0595
