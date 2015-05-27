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
            
        # recalc HCP
        v1 = lx.getValue('LX/SV2/03');
        v2 = lx.getValue('LX/HCP/02')
        lx.setValue(str(float(v1) - float(v2)), 'LX/HCP/03');
        
    clmLoops = ediTemplate.fetchSubNodes("CLM");
    for clm in clmLoops:
        total = clm.getValue('CLM/CLM/02');
        sum1 = 0;
        sum2 = 0;
        lxLoops = clm.fetchSubNodes('LX');
        for lx in lxLoops :
            sum1 += float(lx.getValue('LX/HCP/02'))
            sum2 += float(lx.getValue('LX/HCP/03'))
        clm.setValue(str(sum1), 'CLM/HCP/02');
        clm.setValue(str(sum2), 'CLM/HCP/03');
        if float(total) - (sum1 + sum2) > 0.000001:
            print 'err: total is not match';
            print float(total) - (sum1 + sum2) ;
            clm.showme();
            print sum1 + sum2, sum1, sum2, total, float(total)

        
    stLoops = ediTemplate.fetchSubNodes("ST");       
    for st in stLoops:
        valueLocator = x12edi.ValueLocator('ST/SE/01');
        loopLength = len(st.dump())
        st.tail[-1] = valueLocator.setValue(str(loopLength), st.tail[-1])
        
    for (k, v) in config.items('replace envelope'):
        valueLocator = x12edi.ValueLocator(k.upper());
        loops = ediTemplate.fetchSubNodes(valueLocator.hierarch.levelName);
        for loop in loops:
            loop.setValue(v, k.upper());

            
    ediTemplate.isaNode.showme();

    return ediTemplate.isaNode.dump();



    
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

    
    r = proc(ediTemplate, csvDb, config);
    
    with open('result.txt', 'w') as outputfile:
        for line in r :
            outputfile.write(line+'\n');
        outputfile.close();
    pass