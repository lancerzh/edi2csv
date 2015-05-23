'''
Created on May 20, 2015

@author: lancer
'''
import unittest;

import x12edi;

x12file = "extras/testdata/RHPPAI_0505151403_3.txt";


class TestEdiData(unittest.TestCase):


    def setUp(self):
        with open(x12file, 'rb') as edifile:
            self.x12ediData = edifile.read();
            edifile.close();

    def tearDown(self):
        pass
    
    def testUnpack(self):
        edi = x12edi.createEdi(self.x12ediData);
        self.assertEqual("ISA*00*1         *00*1         *ZZ*TRIZETTOCE     *30*RELIANT        *150505*1405*^*00501*000004221*0*P*:", edi.isaNode.header);
        self.assertEqual("IEA*1*000004221", edi.isaNode.tail[0]);
        self.assertEqual("GS*HC*TRIZETTOCE*RELIANT*20150505*1405*3994734*X*005010X223A2", edi.gsNode.header);
        self.assertEqual("GE*13*3994734", edi.gsNode.tail[0]);

        allTs = edi.getLoops('ST');
        ts = allTs[12]

        self.assertEqual('ST*837*1013*005010X223A2', ts.header);
        self.assertEqual('ST*837*1013*005010X223A2', ts.body[0]);
        self.assertEqual('BHT*0019*00*RELIANT*20150505*1405*CH', ts.body[1]);
        self.assertEqual('NM1*41*2*TRIZETTO*****46*14001', ts.body[2]);
        self.assertEqual('PER*IC*TRIZETTO CLAIMSEXCHANGE*TE*8773667135', ts.body[3]);
        self.assertEqual('NM1*40*2*RELIANT*****46*074', ts.body[4]);
        self.assertEqual('SE*33*1013', ts.tail[0]);
        
        self.assertEqual(1, len(ts.children));
        

    def testGetLoops(self):
        edi = x12edi.createEdi(self.x12ediData);
        
        self.assertEqual(1, len(edi.getLoops('ISA')));
        self.assertEqual(1, len(edi.getLoops('GS')));
        self.assertEqual(13, len(edi.getLoops('ST')));
        self.assertEqual(13, len(edi.getLoops('HL', '20')));
        self.assertEqual(13, len(edi.getLoops('HL', '22')));
        self.assertEqual(10, len(edi.getLoops('HL', '23')));
        self.assertEqual(13, len(edi.getLoops('CLM')));
        self.assertEqual(55, len(edi.getLoops('LX')));
        
        ts = edi.getLoops('ST')[0];
        self.assertEqual(1, len(ts.getLoops('HL', '20')));
        self.assertEqual(1, len(ts.getLoops('HL', '22')));
        self.assertEqual(1, len(ts.getLoops('HL', '23')));
        self.assertEqual(1, len(ts.getLoops('CLM')));
        self.assertEqual(9, len(ts.getLoops('LX')));
        
        ts = edi.getLoops('ST')[12];
        self.assertEqual(1, len(ts.getLoops('HL', '20')));
        self.assertEqual(1, len(ts.getLoops('HL', '22')));
        self.assertEqual(1, len(ts.getLoops('CLM')));
        self.assertEqual(1, len(ts.getLoops('LX')));

    
    def testParent(self):
        self.assertTrue('0500' > '0300')
        edi = x12edi.createEdi(self.x12ediData);
        lx1 = edi.getLoops('LX')[1];
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
                print '  ' * node.deep, node.name,":", node.parent,":", len(node.children), node.header
            else :
                print '  ' * node.deep, node.name,":", node.parent.name,":", len(node.children), node.header
            #print node.dump();
            pass
        '''
        for l in  edi.isaNode.dump() :
            print l;
        '''
        
    def testMatchLoop(self):
        lx1str = """LX*1
SV2*0250**15*UN*1
PWK*OZ*EL***AC*15
DTP*472*D8*20150330
K3*,0,7.5,0,0,0,0,0
        """.strip();
        edi = x12edi.createEdi(self.x12ediData);
        """
        for aLoop in edi.allLoops :
            print aLoop.name, "/", aLoop.dataLines[0];
            for l in aLoop.dataLines:
                print "\t" + l
        """
        #self.assertEqual(13, len(edi.transactions));
        #self.assertEqual(13, len(edi.allLoops));
        conditions = [('LX/LX/01','1')]
        lxLoop = edi.getMatched(conditions);
        print lxLoop;
        self.assertEqual(lx1str, '\n'.join(lxLoop.dump()));
        pass
    
    def testNodeId(self):
        edi = x12edi.createEdi(self.x12ediData);
        self.assertEqual('000004221', edi.getLoops('ISA')[0].id);
        self.assertEqual('3994734', edi.getLoops('GS')[0].id);
        self.assertEqual('1001', edi.getLoops('ST')[0].id);
        self.assertEqual('1', edi.getLoops('HL', '20')[0].id);
        self.assertEqual('2', edi.getLoops('HL', '22')[0].id);
        self.assertEqual('3', edi.getLoops('HL', '23')[0].id);
        self.assertEqual('134150427P00024', edi.getLoops('CLM')[0].id);
        self.assertEqual('1', edi.getLoops('LX')[0].id);


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