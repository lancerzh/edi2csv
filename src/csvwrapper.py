'''
Created on May 19, 2015

@author: lancer
'''

import csv;
import cStringIO;
from re import match;


__CHAR_SEQ__ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
__CHAR_SEQ_LEN__ = len (__CHAR_SEQ__);
__INDEX_MAX_LEN__ = __CHAR_SEQ_LEN__ * (__CHAR_SEQ_LEN__ + 1);
__INDEX_MAPPER__ = {}

def __CREATE_INDEX_MAPPER__(rows):
    for i in range(rows):
        firstPos = i / __CHAR_SEQ_LEN__;
        lastPos = i % __CHAR_SEQ_LEN__;
        key = '';
        if firstPos > 0 :
            key = key + __CHAR_SEQ__[firstPos - 1];
        key = key+__CHAR_SEQ__[lastPos];
        __INDEX_MAPPER__[key] = i;
        #print firstPos, lastPos, key, i;
    return __INDEX_MAPPER__;

__INDEX_MAPPER__ = __CREATE_INDEX_MAPPER__(__INDEX_MAX_LEN__);

def mapIndex(name):
    indexName = '';
    if name.find(':') > 0:
        indexName = name.split(':')[1];
    else :
        indexName = name;
    if indexName.isdigit():
        return int(indexName);
    else :
        return __INDEX_MAPPER__[indexName.upper()]

class CsvDatabase :
    def __init__(self, data, skip=0):
        self.db = [];
        if isinstance(data, str) :
            self.reader = csv.reader(cStringIO.StringIO(data), delimiter=',', quotechar='"', skipinitialspace=True);
        elif isinstance(data, file) :
            self.reader = csv.reader(data, delimiter=',', quotechar='"', skipinitialspace=True);
        else :
            print "err: unknown data type!"
            exit();
        if skip > 0 :
            for i in range(skip) :
                self.reader.next();
        for row in self.reader:
            if row == [] or len(row) < 0 or (len(row) == 1 and row[0] == ''):
                continue;
            self.db.append(row);
            
    
    def getRow(self, index):
        return CsvRow(self.db[index]);
    
    def search(self, conditions):
        result = []
        for row in self.db :
            csvRow = CsvRow(row)
            if csvRow.match(conditions):
                result.append(csvRow) 
        return result;
    
    
    @property
    def length(self):
        return len(self.db);

        
class CsvRow:
    def __init__(self, varlist):
        self.vars = varlist;
        
    def getValue(self, index):
        matchObj = match(r'${(csv.[a-z]+)}' , index);
        #if index
        return self.vars[mapIndex(index)];
        

    def fillVars(self, template):
        pass
    
    def match(self, conditions):
        for key in conditions.keys() :
            if self.vars[mapIndex(key)] != conditions.get(key) :
                return False;
            else :
                continue;
        return True;


if __name__ == '__main__':
    pass