'''
Created on May 18, 2015

@author: lancer
'''

import csv
import ConfigParser

import x12edi


def getMatchItems(s, configFile):
    pass

def getModifyItems(s, configFile):
    pass

def isMatched(matchItems, claim):
    for m in matchItems :
        if not match(claim, m):
            return False;
    return True;


def match(claim, item):
    pass


def modify(claim, item):
    pass


def proc(in_edi, csvfile, config):
    configFile = ConfigParser.RawConfigParser()
    configFile.read(config);
    csvFile = csv.reader(csvfile)
        
    edifile = x12edi(in_edi)
    
    
    
    for line in csvFile:
        matchItems = getMatchItems(line, configFile)
        modifyItems = getModifyItems(line, configFile);
        claim = None
        
        matched = False;
        for claim in edifile.claims():
            if isMatched(matchItems, claim) :
                matched = True;
                break;
        if not matched :
            print "*** never match for :", line;
            exit;
            
        for item in modifyItems:
            modify(claim, item);
     
    ret_edifile = edifile.swapRxTx();
    return ret_edifile



    
if __name__ == '__main__':
    pass