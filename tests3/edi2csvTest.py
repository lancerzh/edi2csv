'''
Created on May 28, 2015

@author: lancer
'''
import unittest
from datetime import date;

from edi2csv import fetchValueWithDefault, Sequence
import x12edi


x12file = "extras/testdata/RHPPAI_0505151403_3.txt";


class Test(unittest.TestCase):


    def setUp(self):
        with open(x12file, 'r') as edifile:
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
        try :
            self.assertIsNone(fetchValueWithDefault(locations, lx));
        except x12edi.ElementNotFoundException as e:
            print(e);
        
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
        try :
            self.assertIsNone(fetchValueWithDefault(locations, lx));
        except x12edi.ElementNotFoundException as e:
            print(e);
        
        locations = "LX/SV2/02-2 or LX/PWK/02-2 or ''"
        self.assertEqual('', fetchValueWithDefault(locations, lx));


        locations = "LX/SV2/02-2 or LX/PWK/02-2 or 'defaultValue'"
        self.assertEqual('defaultValue', fetchValueWithDefault(locations, lx));
        pass
    
    def testDRG(self):
        edi = x12edi.createEdi(self.x12ediData);
        lxloop = edi.fetchSubNodes('LX')[0];
        locations = "CLM/HI*DR/01:02" 
        try :
            self.assertIsNone(fetchValueWithDefault(locations, lxloop));
        except x12edi.ElementNotFoundException as e:
            print(e);
        
        locations = "CLM/HI*DR/01:02 or 'aaaa'" 
        self.assertEqual('aaaa', fetchValueWithDefault(locations, lxloop));
        
    def testSeq(self):
        
        seq = Sequence("JMS${today, '%Y%m%d'}678###");
        now = date.today();
        self.assertEqual('JMS'+ now.strftime('%Y%m%d') + '678001', next(seq))
        
    def testSeqNotKnowVariable(self):
        try :
            Sequence("JMS${date, '%Y%m%d'}678");
        except Exception as e :
            print(e);
    
    def testSeqNotPlaceHolder(self):
        seq = Sequence("JMS678##");
        self.assertEqual('JMS67801', next(seq))
        self.assertEqual('JMS67802', next(seq))
        self.assertEqual('JMS67803', next(seq))
        self.assertEqual('JMS67804', next(seq))
        self.assertEqual('JMS67805', next(seq))
        self.assertEqual('JMS67806', next(seq))
        self.assertEqual('JMS67807', next(seq))
        self.assertEqual('JMS67808', next(seq))
        self.assertEqual('JMS67809', next(seq))
        self.assertEqual('JMS67810', next(seq))
        self.assertEqual('JMS67811', next(seq))
        self.assertEqual('JMS67812', next(seq))

        for i in range(12, 102):
            next(seq);
        self.assertEqual('JMS678103', next(seq))
    
    def testNotPlaceHolder(self):
        seq = Sequence("JMS678");
        self.assertEqual('JMS6781', next(seq))
        for i in range(0, 100):
            next(seq);
        self.assertEqual('JMS678102', next(seq))


        
    def aaatestUnknownLoopName(self):
        edi = x12edi.createEdi(self.x12ediData);
        lxloop = edi.fetchSubNodes('LX')[0];
        locations = "XXX/HI*DR/01:02" 
        self.assertIsNone(fetchValueWithDefault(locations, lxloop));
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()