'''
Created on May 28, 2015

@author: lancer
'''
import unittest

import edi2csv1
import x12edi


x12file = "extras/testdata/RHPPAI_0505151403_3.txt";


class Test(unittest.TestCase):


    def setUp(self):
        with open(x12file, 'rb') as edifile:
            self.x12ediData = edifile.read();
            edifile.close();
            
    def testDefaultValue(self):
        lines = ['LX*1~', 'SV2*0250**15*UN*1~', 'PWK*OZ*EL***AC*15~', 'DTP*472*D8*20150330~', 'K3*,0,7.5,0,0,0,0,0~']
        lx = x12edi.EdiDocNode(lines);
        
        locations = "LX/SV2/02"
        self.assertEqual('', edi2csv1.fetchValueWithDefault(locations, lx));

        locations = "LX/SV2/02-1"
        self.assertEqual('', edi2csv1.fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2"
        self.assertIsNone(edi2csv1.fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2 or ''"
        self.assertEqual('', edi2csv1.fetchValueWithDefault(locations, lx));

        locations = "LX/SV2/02-2 or 'defaultValue'"
        self.assertEqual('defaultValue', edi2csv1.fetchValueWithDefault(locations, lx));
        pass
    
    def testMutiLocator(self):
        #edi = x12edi.createEdi(self.x12ediData);
        lines = ['LX*1~', 'SV2*0250**15*UN*1~', 'PWK*OZ*EL***AC*15~', 'DTP*472*D8*20150330~', 'K3*,0,7.5,0,0,0,0,0~']
        lx = x12edi.EdiDocNode(lines);
        
        locations = "LX/SV2/02-2 or LX/PWK/02"
        self.assertEqual('EL', edi2csv1.fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2 or LX/PWK/02 or ''"
        self.assertEqual('EL', edi2csv1.fetchValueWithDefault(locations, lx));


        locations = "LX/SV2/02-2 or LX/PWK/02 or 'defaultValue'"
        self.assertEqual('EL', edi2csv1.fetchValueWithDefault(locations, lx));
        pass

    def testMutiLocatorDefault(self):
        #edi = x12edi.createEdi(self.x12ediData);
        lines = ['LX*1~', 'SV2*0250**15*UN*1~', 'PWK*OZ*EL***AC*15~', 'DTP*472*D8*20150330~', 'K3*,0,7.5,0,0,0,0,0~']
        lx = x12edi.EdiDocNode(lines);
        
        locations = "LX/SV2/02-2 or LX/PWK/02-2" 
        self.assertIsNone(edi2csv1.fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2 or LX/PWK/02-2 or ''"
        self.assertEqual('', edi2csv1.fetchValueWithDefault(locations, lx));


        locations = "LX/SV2/02-2 or LX/PWK/02-2 or 'defaultValue'"
        self.assertEqual('defaultValue', edi2csv1.fetchValueWithDefault(locations, lx));
        pass
    
    def testDRG(self):
        edi = x12edi.createEdi(self.x12ediData);
        lxloop = edi.fetchSubNodes('LX')[0];
        locations = "CLM/HI*DR/01:02" 
        self.assertIsNone(edi2csv1.fetchValueWithDefault(locations, lxloop));
        
        locations = "CLM/HI*DR/01:02 or 'aaaa'" 
        self.assertEqual('aaaa', edi2csv1.fetchValueWithDefault(locations, lxloop));
        
        
    def aaatestUnknownLoopName(self):
        edi = x12edi.createEdi(self.x12ediData);
        lxloop = edi.fetchSubNodes('LX')[0];
        locations = "XXX/HI*DR/01:02" 
        self.assertIsNone(edi2csv1.fetchValueWithDefault(locations, lxloop));
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()