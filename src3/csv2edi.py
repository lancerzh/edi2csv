'''
Created on May 18, 2015

@author: lancer
'''

from re import match, IGNORECASE
import configparser
import argparse
import os;

import x12edi
import csvwrapper


submitter = ['ST/NM1*41/03',  'GS/GS/02', 'ISA/ISA/06']     #= RELIANT
submitterid = ['ST/NM1*41/09']      # = 074

receiver = ['ST/NM1*40/03', 'GS/GS/03', 'ISA/ISA/08']       # = TRIZETTO
receiverid = ['ST/NM1*40/09']       # = 14001




def recalc_LX_HCP(lx):
    v1 = lx.getValue('LX/SV2/03')
    v2 = lx.getValue('LX/HCP/02')
    lx.setValue(str(float(v1) - float(v2)), 'LX/HCP/03')


def recalc_CLM_HCP(clm):
    total = clm.getValue('CLM/CLM/02')
    sum1 = 0
    sum2 = 0
    lxLoops = clm.fetchSubNodes('LX')
    for lx in lxLoops:
        sum1 += float(lx.getValue('LX/HCP/02'))
        sum2 += float(lx.getValue('LX/HCP/03'))
    
    clm.setValue(str(sum1), 'CLM/HCP/02')
    clm.setValue(str(sum2), 'CLM/HCP/03')
    if float(total) - (sum1 + sum2) > 0.000001:
        print('err: total is not match')
        print(float(total) - (sum1 + sum2))
        clm.showme()
        print(sum1 + sum2, sum1, sum2, total, float(total))


def replace_SE_SEG_NUMBER(st):
    valueLocator = x12edi.ValueLocator('ST/SE/01')
    loopLength = st.segmentLength();
    st.tail[-1] = valueLocator.setValue(str(loopLength), st.tail[-1])


def replaceSubmitterReceiver(template, config):
# set evenlope head
    for k, v in config.items('submitter and receiver'):
        for vl in globals()[k]:
            vl1 = x12edi.ValueLocator(vl)
            loops = template.fetchSubNodes(vl1.hierarch.levelName)
            for l in loops:
                l.replaceValue(v, vl)
'''                
class InsertAction:
    def __init__(self, segment, template):
        self.afterSegment = segment;
        self.template = template;
        
    def perform(self, loop):
        loop.insert(self.template, self.afterSegment);
'''

def proc(template, csvdb, config):
    # do insert
    for (k, v) in config.items('insert segment after'):
        (loopname, segmentPattern) = k.split('/')
        loops = template.fetchSubNodes(loopname);
        for loop in loops:
            loop.insert(v, segmentPattern);
        
    lxLoop = template.fetchSubNodes(config.get('main', 'deepestLoop'));
    for lx in lxLoop :
        conditions = []
        for (k, v) in config.items('keymap'):
            docValue = lx.getValue(k);
            conditions.append((v, docValue));
            #print k, v, docValue

        results = csvdb.search(conditions) ; 
        if len(results) > 1 :
            print("err: expect 1, but get " +  len(results) + " results. Check csv file or keys!")
            for (k, v) in config.items('keymap'):
                print(k, v)
            break;
        if len(results) == 0:
            print("Not found any result.")
            for (k, v) in config.items('keymap'):
                print(k, v)
            continue;
        result = results[0];
        
        # do replace
        for (k, v) in config.items('replace element'):
            #print k, v;
            value = result.getValue(v);
            lx.replaceValue(value, k);
        
        # do append
        for (k, v) in config.items('append element'):
            #print k, v;
            value = result.getValue(v);
            lx.appendValue(value, k);
            
        recalc_LX_HCP(lx)
    
    # recalc CLM/HCP    
    clmLoops = template.fetchSubNodes("CLM");
    for clm in clmLoops:
        recalc_CLM_HCP(clm)

    # recalc st tail lines count
    stLoops = template.fetchSubNodes("ST");       
    for st in stLoops:
        replace_SE_SEG_NUMBER(st)
    
    replaceSubmitterReceiver(ediTemplate, config)      
            
    return template;

def check(config):
    reInsert = r'insert\s+([\'"]?\S+~[\'"]?)\s+after\s+(\S+)';
    reSetvalue = r'setvalue\s+(\$\{csv:[\w]+\})\s+into (\S+)'
    reAppend = r'append\s+(\$\{csv:[\w]+\})\s+at\s+(\S+)'
    '''
    reText = r'[\'"]?[^\$][\w]+[\'"]?'
    reVar = r'[\'"]?\$\{[\w]+\}[\'"]?'
    reCsv = r'[\'"]?\$\{csv:[\w]+\}[\'"]?'
    '''

    config.add_section('insert segment after');
    config.add_section('replace element');
    config.add_section('append element');
    
    #actions = []

    for (k, v) in config.items('actions'):
        kint = int(k);
        print(kint, v)
        matchObj = match(reInsert, v);
        if matchObj != None:
            template = matchObj.group(1).strip(r'[\'" ]')
            locator = matchObj.group(2)
            config.set('insert segment after', locator, template);
            continue;
        matchObj = match(reSetvalue, v);
        if matchObj != None:
            template = matchObj.group(1).strip(r'[\$\{\}\s]')
            locator = matchObj.group(2)

            config.set('replace element', locator, template);
            continue;
        matchObj = match(reAppend, v);
        if matchObj != None:
            template = matchObj.group(1).strip(r'[\$\{\}\s]')
            locator = matchObj.group(2)
            config.set('append element', locator, template);
            continue;
        else :
            print('err: unknown action')
    
    hierarhes = []
    for (k, v) in config.items('keymap'):
        hierarhes.append(x12edi.ValueLocator(k).hierarch);
    hierarhes.sort();
    #print hierarhes[-1].levelName;
    config.set('main', 'deepestLoop', hierarhes[-1].levelName);
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Build an X12 EDi 837 file from a csv db file, base on an edi template file.');
    parser.add_argument('-template', metavar='templatefile', help='edi template file', required=True)
    parser.add_argument('-csv', metavar='csvfile', help='csv db file', required=True)
    parser.add_argument('-cfg', metavar='configfile', help='config file', required=True)
    parser.add_argument('-ediout', metavar='edioutfile', help='edi output file', required=True)

    args = parser.parse_args();
    
    if not os.path.exists(args.template):
        print("input edi template file is not exist. exit...")
        exit;
    if not os.path.exists(args.csv):
        print("input csv db file is not exist. exit...")
        exit;
    if not os.path.exists(args.cfg):
        print("config file is not exist. exit...")
        exit;
    
    edi = None;


    config = configparser.RawConfigParser()
    config.read(args.cfg);
    check(config);
    
    ediTemplate = None;
    with open(args.template, 'rb') as edifile:
        ediTemplate = x12edi.createEdi(edifile.read());
        edifile.close();
    
    csvDb = None;
    csvskip = int(config.get('main', 'csvskipline'));
    with open(args.csv, 'rb') as csvfile:
        csvDb = csvwrapper.CsvDatabase(csvfile, skip = csvskip);
        csvfile.close();
    
    result = proc(ediTemplate, csvDb, config);
    print(result.dump('  ', cr=True));

    with open('result.txt', 'w') as outputfile:
        outputfile.write(result.dump(cr=True));
        outputfile.close();
    pass