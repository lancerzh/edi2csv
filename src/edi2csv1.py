'''
Created on May 22, 2015

@author: lancer
'''

import ConfigParser;
import csv;
import argparse;
import os;

from re import match, search
from string import Template;
from datetime import date;

import x12edi;

class Sequence():
    def __init__(self, template):
        self.count = 0;
        self.prefix = template;
        self.variables = {}
        matchObj = search(r'(\${.*})', template);
        if matchObj != None :
            (fn, para) = matchObj.group(1).strip('${} ').split(',', 2);
            if fn == 'today':
                self.variables['today'] = date.today().strftime(para.strip('[ \'"]'));
                self.prefix = template.replace(matchObj.group(1), '%(today)s');
            else :
                raise Exception(template + ' not know the variables. Please check config file');
        
        matchObj = search(r'(#+)', template);
        if matchObj != None :
            self.prefix = self.prefix.replace(matchObj.group(1), '%(count)' + '0' + str(len(matchObj.group(1))) + 'd');
        else :
            self.prefix = template + '%(count)d'
    
    def next(self):
        self.count += 1;
        self.variables['count'] = self.count;
        return self.prefix % self.variables;


def fetchValueWithDefault(location, loop, msg = ''):
    ls = location.split('or');
    #print ls
    lastLine = ls[-1].strip();
    defaultValue = None;
    if match(r"'.*'", lastLine) != None:
        defaultValue = lastLine.strip("'");
        del ls[-1]
    while len(ls) > 0:
        oneLocation = ls[0].strip();
        del ls[0];
        #print oneLocation
        try :
            return loop.getValue(oneLocation);
        except x12edi.ElementNotFoundException as enfe :
            if len(ls) > 0:
                continue;
            else :
                if defaultValue == None :
                    enfe.msg += " and do not set default value"
                    raise
                return defaultValue;

def proc(edi, config):
    eachby = config.get('main', 'eachby');
    fields = config.items('csv field');
    
    seq = Sequence(config.get('sequence', 'prefix'))
    seqMatch = config.get('sequence', 'match')
    seqMap = {}
    loops = edi.fetchSubNodes(seqMatch.split('/')[0])
    print "total " + str(len(loops)) + " mapped ids"
    for loop in loops :
        trueId = loop.getValue(seqMatch)
        seqMap[trueId] = seq.next();
        print trueId + " map to " + seqMap[trueId];
    
    loops = edi.fetchSubNodes(eachby);
    print "total ", str(len(loops)), eachby, " records."

    varsDict = {}
    data = []

    for loop in loops :
        row = []
        trueId = loop.getValue(seqMatch)
        varsDict['sequence'] = seqMap[trueId]
        for (fieldname, location) in fields :
            if match(r'\$', location):
                t = Template(location)
                value = t.substitute(varsDict);
            elif len(location.strip()) > 0:
                try :
                    value = fetchValueWithDefault(location, loop, fieldname);
                except x12edi.ElementNotFoundException as enfe:
                    print "Field name:", fieldname;
                    print enfe;                
                    value = 'None'
                    
            else :
                # Do not give valueLocator
                value = ''
            if value == None :
                value = 'None'
            if not fieldname.startswith('-') :
                row.append(value);

            varsDict[fieldname.strip('- ')] = value;
        data.append(row);

    return data;

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract X12 EDi 837 file to csv file.');
    parser.add_argument('-edi', metavar='inputfile', help='input edi 837 file', required=True)
    parser.add_argument('-cfg', metavar='configfile', help='config file', required=True)
    parser.add_argument('-csv', metavar='csvfile', help='output csv file', required=True)
    
    args = parser.parse_args();
    
    if not os.path.exists(args.edi):
        print "input edi file is not exist. exit..."
        exit;
    if not os.path.exists(args.cfg):
        print "config file is not exist. exit..."
        exit;
    
    edi = None;

    with open(args.edi, 'rb') as edifile:
        x12ediData = edifile.read();
        edifile.close();
        edi = x12edi.createEdi(x12ediData);
    
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config.read(args.cfg);
                
    data = proc(edi, config);
    
    with open(args.csv, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        row = []
        for (fieldname, location) in config.items('csv field') :
            if not fieldname.startswith('-') :
                row.append(fieldname.strip());
        #print ','.join(row)
        spamwriter.writerow(row);
        
        for aLine in data :
            #print ','.join(aLine)
            spamwriter.writerow(aLine);
        
        csvfile.close();
    pass