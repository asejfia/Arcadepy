'''
Created on Mar 7, 2014

@author: joshua
'''

import csv, re, xlwt
from math import log10,floor

def isAlphanumeric(row):
    rowStr = ''
    for cel in row:
        rowStr = rowStr + cel.strip()
    m = re.search(r"\w",rowStr)
    if m:
        return True
    else:
        return False
    
def roundToN(x,n):
    return round(x, -int(floor(log10(x))) + (n - 1))

if __name__ == '__main__':
    headerRows = {0:[],1:[]}
    with open('/home/joshua/Dropbox/evolution/summary/decay_metrics.csv', 'r') as f:
        outputXlsFilename = '/home/joshua/Dropbox/evolution/summary/decay_metrics.xls'
        book = xlwt.Workbook()
        sheet = book.add_sheet('decay range')
        statNames = ["min","max","mean"]
        reader = csv.reader(f)
        for rowIdx, row in enumerate(reader):
            if isAlphanumeric(row):
                for cellIdx, cell in enumerate(row):
                    stats = {}
                    foundStat = False
                    for statName in statNames:
                        if statName in cell:
                            foundStat = True
                            m = re.search(r'' + statName + ': (-?\d+\.*\d*)', cell.replace("\\n"," "))
                            if m:
                                stats[statName] = m.group(1)
                    if stats:
                        copyCellIdx = 3*(cellIdx-1)+1
                        for statName in statNames:
                            print "{:.3f},".format( float(stats[statName]) ),
                            sheet.write(rowIdx,copyCellIdx,float(stats[statName]))
                            copyCellIdx = copyCellIdx + 1
                    else:
                        print "{0},".format(cell),
                        if rowIdx > 1:
                            sheet.write(rowIdx,cellIdx,cell)
                print
            if rowIdx == 0 or rowIdx == 1:
                for cell in row:
                    if cell.strip():
                            headerRows[rowIdx].append(cell.strip())
        headerShift = {0:6,1:3}
        for rowIdx,row in headerRows.iteritems():
            for elemIdx,elem in enumerate(row):
                sheet.write_merge(rowIdx,rowIdx,elemIdx*headerShift[rowIdx]+1,elemIdx*headerShift[rowIdx]+headerShift[rowIdx],elem)
        book.save(outputXlsFilename)