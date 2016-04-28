'''
Created on May 20, 2015

@author: lancer
'''
import unittest;
import re

import x12edi;
from x12edi import HierarchLocator;
from x12edi import ValueLocator;



x12file = "extras/testdata/RHPPAI_0505151403_3.txt";


class TestEdiData(unittest.TestCase):


    def setUp(self):
        with open(x12file, 'r') as edifile:
            self.x12ediData = edifile.read();
            edifile.close();

    def tearDown(self):
        pass
    
    def testHierarchLocator(self):
        self.assertEqual(HierarchLocator('ISA'), HierarchLocator('ISA*00*1         *00*1         *ZZ*TRIZETTOCE     *30*RELIANT        *150505*1405*^*00501*000004220*0*P*:~'));
        self.assertEqual(HierarchLocator('GS'), HierarchLocator('GS*HC*TRIZETTOCE*RELIANT*20150505*1405*3994733*X*005010X222A1~'));
        self.assertEqual(HierarchLocator('ST'), HierarchLocator('ST*837*1001*005010X222A1~'));
        self.assertEqual(HierarchLocator('HL:20'), HierarchLocator('HL*1**20*1~'));
        self.assertEqual(HierarchLocator('HL:22'), HierarchLocator('HL*2*1*22*1~'));
        self.assertEqual(HierarchLocator('HL:23'), HierarchLocator('HL*3*2*23*0~'));    
        self.assertEqual(HierarchLocator('CLM'), HierarchLocator('CLM*5837*80***11:B:1*Y*A*Y*I~'));    
        self.assertEqual(HierarchLocator('LX'), HierarchLocator('LX*1~'));
        
        try :
            HierarchLocator('UNKNOWN_LOOP')
        except KeyError as e:
            print(e);
        

    def testHierarchLocatorCompare(self):
        self.assertEqual(HierarchLocator('HL'), HierarchLocator('HL'));
        self.assertEqual(HierarchLocator('HL'), HierarchLocator('HL:20'));
        self.assertTrue(HierarchLocator('HL:20') < HierarchLocator('HL:22'));
        self.assertTrue(HierarchLocator('HL:22') < HierarchLocator('HL:23'));

        self.assertTrue(HierarchLocator('ISA') < HierarchLocator('GS'));
        self.assertTrue(HierarchLocator('GS') < HierarchLocator('ST'));

        self.assertTrue(HierarchLocator('ST') < HierarchLocator('HL'));
        self.assertTrue(HierarchLocator('HL') < HierarchLocator('CLM'));
        self.assertTrue(HierarchLocator('HL:23') < HierarchLocator('CLM'));
        self.assertTrue(HierarchLocator('CLM') < HierarchLocator('LX'));
        
    def testReMatch(self):
        matchStr = r'([0-9]+)([,:]?)([0-9]*)'
        matchObj = re.match(matchStr , '01:09')
        self.assertEqual('01', matchObj.group(1));
        self.assertEqual(':', matchObj.group(2));
        self.assertEqual('09', matchObj.group(3));
        
        matchObj = re.match( matchStr, '01,09')
        self.assertEqual('01', matchObj.group(1));
        self.assertEqual(',', matchObj.group(2));
        self.assertEqual('09', matchObj.group(3));
        
        matchObj = re.match( matchStr, '01')
        self.assertEqual('01', matchObj.group(1));
        self.assertEqual('', matchObj.group(2));
        self.assertEqual('', matchObj.group(3));


    
    def testValueLocator(self):
        self.assertEqual(2, ValueLocator('ST/ST/02').elementPos);
        self.assertEqual(2, ValueLocator('CLM/REF*D9/02').elementPos );
        self.assertEqual(1, ValueLocator('HL/HL/01').elementPos );
        
        self.assertEqual(9, ValueLocator('HL:22/NM1*IL/09').elementPos);
        self.assertFalse(ValueLocator('HL:22/NM1*IL/09').hasSubElement());
        self.assertTrue(ValueLocator('HL:22/NM1*IL/09:01').hasSubElement());
        self.assertTrue(ValueLocator('HL:22/NM1*IL/09,01').hasSubElement());


        self.assertEqual(2, ValueLocator('CLM/HI*BF/02:3').elementPos);
        self.assertEqual(4, ValueLocator('CLM/HI*BF/02:4').subElementPos);
        self.assertEqual(1, ValueLocator('LX/SV2/01,5').elementPos);
        self.assertEqual(5, ValueLocator('LX/SV2/01,5').subElementPos);
        
        self.assertEqual(3, ValueLocator('LX/SV2/03/6').elementPos);
        self.assertEqual(6, ValueLocator('LX/SV2/03/6').subElementPos);
        pass
    
    
    def testEnvelopes(self):
        ''' include ISA, GS, ST three envelopes
        '''
        edi = x12edi.createEdi(self.x12ediData);
        self.assertEqual("ISA*00*1         *00*1         *ZZ*TRIZETTOCE     *30*RELIANT        *150505*1405*^*00501*000004221*0*P*:~", edi.isaNode.header);
        self.assertEqual("IEA*1*000004221~", edi.isaNode.tail[0]);
        self.assertEqual("GS*HC*TRIZETTOCE*RELIANT*20150505*1405*3994734*X*005010X223A2~", edi.gsNode.header);
        self.assertEqual("GE*13*3994734~", edi.gsNode.tail[0]);

        allTs = edi.fetchSubNodes('ST');
        ts = allTs[12]

        self.assertEqual('ST*837*1013*005010X223A2~', ts.header);
        self.assertEqual('ST*837*1013*005010X223A2~', ts.body[0]);
        self.assertEqual('BHT*0019*00*RELIANT*20150505*1405*CH~', ts.body[1]);
        self.assertEqual('NM1*41*2*TRIZETTO*****46*14001~', ts.body[2]);
        self.assertEqual('PER*IC*TRIZETTO CLAIMSEXCHANGE*TE*8773667135~', ts.body[3]);
        self.assertEqual('NM1*40*2*RELIANT*****46*074~', ts.body[4]);
        self.assertEqual('SE*33*1013~', ts.tail[0]);
        
        self.assertEqual(1, len(ts.children));
        

    def testGetChildren(self):
        ''' get children by hierarch level
        '''
        edi = x12edi.createEdi(self.x12ediData);
        
        self.assertEqual(1, len(edi.fetchSubNodes('ISA')));
        self.assertEqual(1, len(edi.fetchSubNodes('GS')));
        self.assertEqual(13, len(edi.fetchSubNodes('ST')));
        self.assertEqual(13, len(edi.fetchSubNodes('HL:20')));
        self.assertEqual(13, len(edi.fetchSubNodes('HL:22')));
        self.assertEqual(10, len(edi.fetchSubNodes('HL:23')));
        self.assertEqual(13, len(edi.fetchSubNodes('CLM')));
        self.assertEqual(55, len(edi.fetchSubNodes('LX')));
        
        ts = edi.fetchSubNodes('ST')[0];
        self.assertEqual(1, len(ts.fetchSubNodes('HL:20')));
        self.assertEqual(1, len(ts.fetchSubNodes('HL:22')));
        self.assertEqual(1, len(ts.fetchSubNodes('HL:23')));
        self.assertEqual(1, len(ts.fetchSubNodes('CLM')));
        self.assertEqual(9, len(ts.fetchSubNodes('LX')));
        
        ts = edi.fetchSubNodes('ST')[12];
        self.assertEqual(1, len(ts.fetchSubNodes('HL:20')));
        self.assertEqual(1, len(ts.fetchSubNodes('HL:22')));
        self.assertEqual(1, len(ts.fetchSubNodes('CLM')));
        self.assertEqual(1, len(ts.fetchSubNodes('LX')));

    
    def testParent(self):
        ''' fatch parent
        '''
        self.assertTrue('0500' > '0300')
        edi = x12edi.createEdi(self.x12ediData);
        lx1 = edi.fetchSubNodes('LX')[1];
        self.assertEqual('CLM', lx1.parent.name)
        self.assertEqual('HL', lx1.parent.parent.name)
        self.assertEqual('HL', lx1.parent.parent.parent.name)
        self.assertEqual('HL', lx1.parent.parent.parent.parent.name)
        self.assertEqual('ST', lx1.parent.parent.parent.parent.parent.name)
        self.assertEqual('GS', lx1.parent.parent.parent.parent.parent.parent.name)
        self.assertEqual('ISA', lx1.parent.parent.parent.parent.parent.parent.parent.name)
        self.assertIsNone(lx1.parent.parent.parent.parent.parent.parent.parent.parent)

        
    def testTraverse(self):
        ''' just print whole document, show the hierarch
        '''
        edi = x12edi.createEdi(self.x12ediData);
        for node in edi.traverse():
            if node.parent == None:
                print('  ' * node.deep, node.name,":", node.parent,":", len(node.children), node.header)
            else :
                print('  ' * node.deep, node.name,":", node.parent.name,":", len(node.children), node.header)
            pass      
        print(edi.dump());
        print(edi.dump('  '))  
        print(edi.dump('', False))  
        
    def testBug(self):
        edi = x12edi.createEdi(self.x12ediData);
        self.assertEqual('2', edi.fetchSubNodes('HL:22')[0].id);
    
    def testNodeId(self):
        edi = x12edi.createEdi(self.x12ediData);
        self.assertEqual('000004221', edi.fetchSubNodes('ISA')[0].id);
        self.assertEqual('3994734', edi.fetchSubNodes('GS')[0].id);
        self.assertEqual('1001', edi.fetchSubNodes('ST')[0].id);
        self.assertEqual('1', edi.fetchSubNodes('HL:20')[0].id);
        self.assertEqual('2', edi.fetchSubNodes('HL:22')[0].id);
        self.assertEqual('3', edi.fetchSubNodes('HL:23')[0].id);
        self.assertEqual('134150427P00024', edi.fetchSubNodes('CLM')[0].id);
        self.assertEqual('1', edi.fetchSubNodes('LX')[0].id);
        
    def testExceptValue(self):
        edi = x12edi.createEdi(self.x12ediData);
        exampleLoop = edi.fetchSubNodes('LX')[12];
        tsLoop = exampleLoop.getParent('ST');
        print(tsLoop);
        try :
            exampleLoop.getValue("LX/SV2/02-02");
        except x12edi.ElementNotFoundException as e:
            print(e);
            self.assertTrue(e.msg.startswith('Not Found Element'))
        try :
            exampleLoop.getValue("LX/SV1/02-02");
        except x12edi.ElementNotFoundException as e:
            print(e);
            self.assertTrue(e.msg.startswith('Not Found Segment'))
        try :
            exampleLoop.getValue("HL:23/NM1*IL/03");
        except x12edi.ElementNotFoundException as e:
            print(e);
            self.assertTrue(e.msg.startswith('Not Found Loop'))


    def testSplit(self):
        ''' Language test
        '''
        pattern = 'CLM/REF*D9/02'
        [patternName, segHeader, elementPos]  = pattern.split('/');
        self.assertEqual('CLM', patternName);
        self.assertEqual('REF*D9', segHeader);
        self.assertEqual('02', elementPos);
        
        pattern = 'CLM/REF*D9/'
        [patternName, segHeader, elementPos]  = pattern.split('/');
        self.assertEqual('CLM', patternName);
        self.assertEqual('REF*D9', segHeader);
        self.assertEqual('', elementPos);
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()