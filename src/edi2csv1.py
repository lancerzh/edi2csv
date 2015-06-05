'''
Created on May 22, 2015

@author: lancer
'''

import ConfigParser;
from re import match, split
from string import Template;

import x12edi;

x12file = "extras/testdata/RHPPAI_0505151403_3.txt";
x12ediData = None;




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
        except IndexError as ie:
            if len(ls) > 0:
                continue;
            else :
                if defaultValue == None :
                    print "**** field name" + msg;
                    print location;
                    #print ie.msg;                
                return defaultValue;

def proc():
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
        for index, (fieldname, location) in enumerate(fields) :
            if match(r'\$', location):
                t = Template(location)
                '''
                for i in range(index):
                    print title[i], myvars[title[i]]
                    '''
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