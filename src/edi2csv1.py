'''
Created on May 22, 2015

@author: lancer
'''

import ConfigParser;
from re import match, search
from string import Template;
from datetime import date;

import x12edi;

x12file = "extras/testdata/RHPPAI_0505151403_3.txt";
x12ediData = None;

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
            value = loop.getValue(oneLocation);
            return value;

        except x12edi.ElementNotFoundException as enfe :
            if len(ls) > 0:
                continue;
            else :
                if defaultValue == None :
                    print "**** field name" + msg;
                    print location;
                    print enfe;                
                return defaultValue;

def proc():
    myseq = {}
    seq = Sequence(seqItems.get('prefix'))
    loops = edi.fetchSubNodes(seqItems.get('match').split('/')[0])
    for loop in loops :
        trueId = loop.getValue(seqItems.get('match'))
        myseq[trueId] = seq.next();
    
    title = [];
    ifOutput = [];
    
    for (fieldname, location) in fields :
        title.append(fieldname.strip('- '));
        if not fieldname.startswith('-') :
            ifOutput.append('+')
        else :
            ifOutput.append('-')

    myvars = {}
    data = []
    loops = edi.fetchSubNodes(eachby);
    for loop in loops :
        row = []
        trueId = loop.getValue(seqItems.get('match'))
        myvars['sequence'] = myseq[trueId]
        for index, (fieldname, location) in enumerate(fields) :
            if match(r'\$', location):
                t = Template(location)
                value = t.substitute(myvars);
            elif len(location.strip()) > 0:
                value = fetchValueWithDefault(location, loop, fieldname);
            else :
                value = ''
            if value == None :
                value = 'None'
            row.append(value);
            myvars[title[index]] = value;
        data.append(row);
        
    
    return (title, data, ifOutput);



if __name__ == '__main__':
    with open(x12file, 'rb') as edifile:
        x12ediData = edifile.read();
        edifile.close();
    edi = x12edi.createEdi(x12ediData);
    
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config.read('to_reliant_csv.ini');
                
    eachby = config.get('main', 'eachby');
    
    fields = config.items('csv field');

    seqItems = {}
    seqItems['prefix'] = config.get('sequence', 'prefix');
    seqItems['match'] = config.get('sequence', 'match');
    
    (title, data, ifOutput) = proc();
    
    row = []
    for index, ifo in enumerate(ifOutput) :
        if ifo != '-':
            row.append(title[index]);
    print ', '.join(row);

    for aLine in data :
        row = []
        for index, ifo in enumerate(ifOutput) :
            if ifo != '-':
                row.append(aLine[index]);
        print ', '.join(row);

    pass