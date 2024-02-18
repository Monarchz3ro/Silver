'''
quick and dirty tabulator.
it'll do.
'''
def tabulate(table: tuple[list[str]], delim:str="|"):
    number_columns = len(table[0])
    column_max = []
    for _ in range(number_columns):
        column_max.append(0)

    #check if the rows are of equal length
    for row in table:
        if len(row) != number_columns: 
            print("All rows must be of equal length.")
            return
    
    #find the max length of each column
    for row in table:
        for irow,item in enumerate(row):
            if len(str(item)) > column_max[irow]:
                column_max[irow] = len(str(item))
    
    #fill in padding into the items
    ret = table
    for icolumn,row in enumerate(ret):
        for irow,item in enumerate(row):
            offset = column_max[irow] - len(str(item)) 
            ret[icolumn][irow] = str(ret[icolumn][irow]) + (" "*offset)
    
    delim = f" {delim} "

    #throw output
    for row in ret:
        print(delim.join(row))