'''
Created on May 22, 2015

@author: lancer
'''

import ConfigParser;

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
            value = loop.getValue(location);
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