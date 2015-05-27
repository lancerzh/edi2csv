'''
Created on May 18, 2015

@author: lancer
'''

import csv
import ConfigParser

import x12edi
import csvwrapper



def proc(ediTemplate, csvdb, config):
    
    # do insert
    for (k, v) in config.items('insert segment after'):
        (loopname, segmentPattern) = k.upper().split('/')
        loops = ediTemplate.fetchSubNodes(loopname);
        for loop in loops:
            loop.insert(v.upper(), segmentPattern);
        
        
    
    lxLoop = ediTemplate.fetchSubNodes("LX");
    
    for lx in lxLoop :
        conditions = []
        for (k, v) in config.items('keys'):
            docValue = lx.getValue(k.upper());
            conditions.append((v, docValue));
            #print k, v, docValue

        results = csvdb.search(conditions) ; 
        if len(results) > 1 :
            print "err: expect 1, but get " +  len(results) + " results. Check csv file or keys!"
            for (k, v) in config.items('keys'):
                print k, v
            break;
        if len(results) == 0:
            print "Not found any result."
            for (k, v) in config.items('keys'):
                print k, v
            continue;
        result = results[0];
        
        # do replace
        for (k, v) in config.items('replace element'):
            #print k, v;
            value = result.getValue(v);
            lx.replaceValue(value, k.upper());
        
        # do append
        for (k, v) in config.items('append element'):
            #print k, v;
            value = result.getValue(v);
            lx.appendValue(value, k.upper());
            
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