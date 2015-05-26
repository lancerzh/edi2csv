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
        
    edifile = x12edi.EdiDoc(in_edi)
    
    lxLoop = edifile.getChilerenNodes("LX");
    
    for lx in lxLoop :
        
        matchItems = getMatchItems(lx, configFile)
        modifyItems = getModifyItems(lx, configFile);
        line = None
        
        matched = False;
        for line in csvFile.lines():
            if isMatched(matchItems, line) :
                matched = True;
                break;
        if not matched :
            print "*** never match for :", lx.dump();
            exit;
            
        for item in modifyItems:
            modify(lx, item);
     
    ret_edifile = edifile.swapRxTx();
    return ret_edifile



    
if __name__ == '__main__':
    pass