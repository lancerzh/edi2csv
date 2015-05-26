'''
Created on May 18, 2015

@author: lancer
'''

import csv
import ConfigParser

import x12edi
import csvwrapper


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


def proc(ediTemplate, csvdb, config):
    
    conditions = {}
    for (k, v) in config.items('keys'):
        conditions[k.upper()] = v.upper();
    
    insertDefinition = {}
    for (k, v) in config.items('insert segment after'):
        insertDefinition[k.upper()] = v.upper();
    
    replaceDefinition = {}
    for (k, v) in config.items('replace element'):
        replaceDefinition[k.upper()] = v.upper();
    
    appendDefinition = {}
    for (k, v) in config.items('append element'):
        appendDefinition[k.upper()] = v.upper();
    
    # do insert
    for hl in insertDefinition.keys():
        (loopname, segmentPattern) = hl.split('/')
        loops = ediTemplate.fetchSubNodes(loopname);
        for loop in loops:
            loop.insert(insertDefinition.get(hl), segmentPattern);
        
        
    
    lxLoop = ediTemplate.fetchSubNodes("LX");
    
    for lx in lxLoop :
        searchConditions = {};
        for key in conditions.keys():
            searchConditions[conditions.get(key)] =  lx.getValue(key);
        results = csvdb.search(searchConditions) ; 
        if len(results) > 1 :
            print "err: expect 1, but get " +  len(results) + " results. Check csv file or keys!"
            for key in conditions.keys():
                print key, conditions.get(key)
            for key in searchConditions.keys():
                print key, searchConditions.get(key)
            break;
        if len(results) == 0:
            print "Not found any result."
            for key in conditions.keys():
                print key, conditions.get(key)
            for key in searchConditions.keys():
                print key, searchConditions.get(key)
            continue;
        result = results[0];
        
        # do insert
        for hl in replaceDefinition.keys():
            value = result.getValue(replaceDefinition.get(hl));
            lx.replaceValue(value, hl);
            
        modifyItems = getModifyItems(lx, config);
        
    ediTemplate.isaNode.showme();

    return ;



    
if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('from_reliant_csv.ini');
    ediTemplate = None;
    ediTemplateFile = 'extras/testdata/RHPPAI_0505151403_3.txt';
    with open(ediTemplateFile, 'rb') as edifile:
        x12ediData = edifile.read();
        ediTemplate = x12edi.createEdi(x12ediData);
        edifile.close();
    csvDb = None;
    csvfilename = 'extras/testdata/JMS_RELIANT_I_20150505output.csv'
    with open(csvfilename, 'rb') as csvfile:
        csvDb = csvwrapper.CsvDatabase(csvfile, skip = 1);

    
    proc(ediTemplate, csvDb, config);
    pass