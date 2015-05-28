'''
Created on May 22, 2015

@author: lancer
'''

import ConfigParser;
from re import match;

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
    data = []
    row = []
    loops = edi.fetchSubNodes(eachby);
    for loop in loops :
        for (fieldname, location) in fields :
            if len(location.strip()) > 0:
                value = fetchValueWithDefault(location, loop, fieldname);
            else :
                value = ''
            if value == None :
                value = 'None'
            row.append(value);
        data.append(row);
        row = [];
        title = []    
        
    for (fieldname, location) in fields :
        title.append(fieldname);
    print ', '.join(title);

    for r in data :
        print ', '.join(r);



if __name__ == '__main__':
    with open(x12file, 'rb') as edifile:
        x12ediData = edifile.read();
        edifile.close();
    edi = x12edi.createEdi(x12ediData);
    
    config = ConfigParser.RawConfigParser()
    config.read('to_reliant_csv.ini');
    eachby = config.get('main', 'eachby');
    
    fields = config.items('csv field');
    
    proc();
    pass