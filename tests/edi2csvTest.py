'''
Created on May 28, 2015

@author: lancer
'''
import unittest
from datetime import date;

from edi2csv1 import fetchValueWithDefault, Sequence
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
        self.assertEqual('', fetchValueWithDefault(locations, lx));

        locations = "LX/SV2/02-1"
        self.assertEqual('', fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2"
        self.assertIsNone(fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2 or ''"
        self.assertEqual('', fetchValueWithDefault(locations, lx));

        locations = "LX/SV2/02-2 or 'defaultValue'"
        self.assertEqual('defaultValue', fetchValueWithDefault(locations, lx));
        pass
    
    def testMutiLocator(self):
        #edi = x12edi.createEdi(self.x12ediData);
        lines = ['LX*1~', 'SV2*0250**15*UN*1~', 'PWK*OZ*EL***AC*15~', 'DTP*472*D8*20150330~', 'K3*,0,7.5,0,0,0,0,0~']
        lx = x12edi.EdiDocNode(lines);
        
        locations = "LX/SV2/02-2 or LX/PWK/02"
        self.assertEqual('EL', fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2 or LX/PWK/02 or ''"
        self.assertEqual('EL', fetchValueWithDefault(locations, lx));


        locations = "LX/SV2/02-2 or LX/PWK/02 or 'defaultValue'"
        self.assertEqual('EL', fetchValueWithDefault(locations, lx));
        pass

    def testMutiLocatorDefault(self):
        #edi = x12edi.createEdi(self.x12ediData);
        lines = ['LX*1~', 'SV2*0250**15*UN*1~', 'PWK*OZ*EL***AC*15~', 'DTP*472*D8*20150330~', 'K3*,0,7.5,0,0,0,0,0~']
        lx = x12edi.EdiDocNode(lines);
        
        locations = "LX/SV2/02-2 or LX/PWK/02-2" 
        self.assertIsNone(fetchValueWithDefault(locations, lx));
        
        locations = "LX/SV2/02-2 or LX/PWK/02-2 or ''"
        self.assertEqual('', fetchValueWithDefault(locations, lx));


        locations = "LX/SV2/02-2 or LX/PWK/02-2 or 'defaultValue'"
        self.assertEqual('defaultValue', fetchValueWithDefault(locations, lx));
        pass
    
    def testDRG(self):
        edi = x12edi.createEdi(self.x12ediData);
        lxloop = edi.fetchSubNodes('LX')[0];
        locations = "CLM/HI*DR/01:02" 
        self.assertIsNone(fetchValueWithDefault(locations, lxloop));
        
        locations = "CLM/HI*DR/01:02 or 'aaaa'" 
        self.assertEqual('aaaa', fetchValueWithDefault(locations, lxloop));
        
    def testSeq(self):
        
        seq = Sequence("JMS${today, '%Y%m%d'}678###");
        now = date.today();
        self.assertEqual('JMS'+ now.strftime('%Y%m%d') + '678001', seq.next())
        
    def testSeqNotKnowVariable(self):
        try :
            Sequence("JMS${date, '%Y%m%d'}678");
        except Exception as e :
            print e;
    
    def testSeqNotPlaceHolder(self):
        seq = Sequence("JMS678##");
        self.assertEqual('JMS67801', seq.next())
        self.assertEqual('JMS67802', seq.next())
        self.assertEqual('JMS67803', seq.next())
        self.assertEqual('JMS67804', seq.next())
        self.assertEqual('JMS67805', seq.next())
        self.assertEqual('JMS67806', seq.next())
        self.assertEqual('JMS67807', seq.next())
        self.assertEqual('JMS67808', seq.next())
        self.assertEqual('JMS67809', seq.next())
        self.assertEqual('JMS67810', seq.next())
        self.assertEqual('JMS67811', seq.next())
        self.assertEqual('JMS67812', seq.next())

        for i in range(12, 102):
            seq.next();
        self.assertEqual('JMS678103', seq.next())
    
    def testNotPlaceHolder(self):
        seq = Sequence("JMS678");
        self.assertEqual('JMS6781', seq.next())
        for i in range(0, 100):
            seq.next();
        self.assertEqual('JMS678102', seq.next())


        
    def aaatestUnknownLoopName(self):
        edi = x12edi.createEdi(self.x12ediData);
        lxloop = edi.fetchSubNodes('LX')[0];
        locations = "XXX/HI*DR/01:02" 
        self.assertIsNone(fetchValueWithDefault(locations, lxloop));
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()