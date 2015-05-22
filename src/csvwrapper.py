'''
Created on May 19, 2015

@author: lancer
'''

import csv;
import cStringIO;

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
        self.maxRows = -1;
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
    
    def get_value(self, pattern):
        index = mapIndex(pattern);
        if index >= self.maxRows:
            print "err: index is bigger:", index, self.maxRows
        return self.currentData[index];

    
    def next(self):
        """ next line
        """
        self.currentData = self.reader.next();
        print self.currentData
        if self.maxRows < 0:
            self.maxRows = len(self.currentData)
        





if __name__ == '__main__':
    pass