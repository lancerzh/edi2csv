'''
Created on May 22, 2015

@author: lancer
'''

import ConfigParser;
from re import match;

import x12edi;

x12file = "extras/testdata/RHPPAI_0505151403_3.txt";
x12ediData = None;

with open(x12file, 'rb') as edifile:
    x12ediData = edifile.read();
    edifile.close();
edi = x12edi.createEdi(x12ediData);

config = ConfigParser.RawConfigParser()
config.read('to_reliant_csv.ini');
eachby = config.get('main', 'eachby');

fields = config.items('csv field');

title = []    
for (fieldname, location) in fields :
    title.append(fieldname);
print ', '.join(title);

data = []
row = []

loops = edi.fetchSubNodes(eachby);
for loop in loops :
    for (fieldname, location) in fields :
        if len(location) > 0:
            ls = location.split('or');
            while len(ls) > 0:
                oneLocation = ls.pop().strip();
                if match(r'\'.*\'', oneLocation) != None:
                    value = oneLocation.strip('\'');
                    break;
                try :
                    value = loop.getValue(oneLocation);
                    if value != None and len(value) > 0:
                        break;
                except IndexError as ie:
                    print fieldname;
                    print location;
                    print ie.msg.dump();
                    value = '';
                    if len(ls) > 0:
                        oneLocation = ls[-1].strip();
                        if match(r'\'.*\'', oneLocation) != None:
                            value = oneLocation.strip('\'');
                        else :
                            print fieldname;
                            print location;
                            print ie.msg.dump();
                            value = '';
                    else :
                        print fieldname;
                        print location;
                        print ie.msg.dump();
                        value = '';
        else :
            value = ''
        if value == None :
            value = ''
        row.append(value);
    data.append(row);
    row = [];

for r in data :
    print ', '.join(r);



if __name__ == '__main__':
    pass