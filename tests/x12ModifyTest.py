'''
Created on May 26, 2015

@author: lancer
'''
import unittest
from string import Template;
from re import match;

import x12edi;


x12file = "extras/testdata/RHPPAI_0505151403_3.txt";


class Test(unittest.TestCase):


    def setUp(self):
        with open(x12file, 'rb') as edifile:
            self.x12ediData = edifile.read();
            edifile.close();
            

    def tearDown(self):
        pass
    
    def testTemplete(self):
        template = Template('NTE*ADD*${l},${m}~');
        mymap = {'l':'10', 'm':'20'};
        self.assertEqual('NTE*ADD*10,20~',  template.safe_substitute(mymap));
        pass
        
    def testInsert(self):
        edi = x12edi.createEdi(self.x12ediData);
        lx = edi.fetchSubNodes('LX')[0];
        clm = lx.getParent('CLM');
        print lx;
        print clm;
        lx.insert('NTE*ADD*${csv:l},${csv:m}~', 'K3');
        lx.insert('HCP*02*${csv:k}**RELIANT~', 'NTE*ADD');
        clm.insert("NTE*ADD*${csv:n}~", 'REF*EA');
        clm.insert("HCP*02***RELIANT~", 'HI');
        print lx;
        print clm;
        
    def testSetValue(self):
        node = x12edi.EdiDocNode(['LX*1~', 'SV1*HC:99443:::::PHYS/QHP TELEPHONE EVALUATION 21-30 MIN*80*UN*1***1~']);
        node.setValue('aaa', 'LX/SV1/01')
        self.assertEqual('SV1*aaa*80*UN*1***1~', node.body[1])
        
        node = x12edi.EdiDocNode(['LX*1~', 'SV1*HC:99443:::::*80*UN*1***1~']);
        node.setValue('aaa', 'LX/SV1/01:3')
        self.assertEqual('SV1*HC:99443:aaa::::*80*UN*1***1~', node.body[1])
        
    def testMatch(self):
        r = r'(csv:\w+)(,(csv:\w+))*'
        self.assertIsNotNone(match(r, 'csv:a,csv:b'))
        self.assertIsNotNone(match(r, 'csv:a,csv:b,csv:c'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()