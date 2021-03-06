'''
Created on May 19, 2015

@author: lancer
'''
import unittest

import csv;
from re import match;


import csvwrapper;

csvfilename = "extras/testdata/JMS_RELIANT_I_20150505output.csv";




class Test(unittest.TestCase):
    
    def setUp(self):
        with open(csvfilename, 'rb') as csvfile:
            self.csvDb = csvwrapper.CsvDatabase(csvfile, skip = 1);
        pass;

    def tearDown(self):
        pass     
    
    def testIsCurrency(self):
        self.assertTrue('120'.isdigit());
        self.assertFalse('120.00'.isdigit());
        
        self.assertTrue(csvwrapper.isCurrency('$10.56'));
        self.assertTrue(csvwrapper.isCurrency('$1,000.45'));
        self.assertTrue(csvwrapper.isCurrency('$10,000,000.0'));
        self.assertTrue(csvwrapper.isCurrency('0.56'));
        self.assertTrue(csvwrapper.isCurrency('1,000.45'));
        self.assertTrue(csvwrapper.isCurrency('10,000,000.0'));

        self.assertFalse(csvwrapper.isCurrency('$$10.56'));
        self.assertFalse(csvwrapper.isCurrency('$a10.56'));
        self.assertFalse(csvwrapper.isCurrency('a$10.56'));
        self.assertFalse(csvwrapper.isCurrency('a10.56'));
        self.assertFalse(csvwrapper.isCurrency('10.56a'));

        self.assertTrue(csvwrapper.isCurrency('$120.50'));

        row = '$120.50,aaa,bbb'
        csvRow = csvwrapper.CsvRow(row.split(','));
        self.assertEqual('120.50', csvRow.getValue('a'));


    def testSearch(self):
        result = self.csvDb.search([('csv:b','134150427P00022')]);
        self.assertEqual(15, len(result))
        
        result = self.csvDb.search([('csv:c', '8')]);
        self.assertEqual(3, len(result))
        
        result = self.csvDb.search([('csv:b','134150427P00022'), ('csv:c','8')]);
        self.assertEqual(1, len(result))
                
    def testFileRead(self):
        self.assertEqual(55, self.csvDb.length)
        
    def testSkipAndSpace(self):
        inputLine = """EOR ID,OriginalClaim ID,Line ID, aaa
        
        48377, 134150427P00024, 1, "aaa"\n
        """
        csvDb = csvwrapper.CsvDatabase(inputLine, 1);
        
        #self.assertEqual(1, csvDb.length());
        row = csvDb.getRow(0);
        self.assertEqual('48377', row.getValue('csv:a'))
        self.assertEqual('134150427P00024', row.getValue('csv:b'))
        self.assertEqual('1', row.getValue('csv:c'))
        self.assertEqual('aaa', row.getValue('csv:d'))
        
        
    def testCsvRow(self):
        inputLine = "48377,134150427P00024,1,250,173230,,,,1,$15.00,$10.00,RVC,SND,RVC - Reimbursement from objective validation of nationally accepted billing and coding guidelines"
        csvRow = csvwrapper.CsvRow(inputLine.split(','));  # test skip here

        self.assertEqual('134150427P00024', csvRow.getValue('b'))
        self.assertEqual('1', csvRow.getValue('c'))
        self.assertEqual('10.00', csvRow.getValue('K'))
        self.assertEqual('RVC', csvRow.getValue('csv:l'))
        self.assertEqual('SND', csvRow.getValue('m'))
        self.assertEqual('RVC - Reimbursement from objective validation of nationally accepted billing and coding guidelines', csvRow.getValue('n'))

    def testMatch(self):
        index = '${csv:a}'
        matchObj = match(r'\$\{(csv.[a-z]+)\}' , index);
        print matchObj.group(0);
        
    
    def testMapIndex(self):
        #print csvwrapper.__INDEX_MAPPER__;
        
        self.assertEqual(0, csvwrapper.mapIndex('A'));
        self.assertEqual(0, csvwrapper.mapIndex('a'));
        self.assertEqual(0, csvwrapper.mapIndex('0'));
        self.assertEqual(0, csvwrapper.mapIndex('csv:A'));
        
        self.assertEqual(25, csvwrapper.mapIndex('Z'));
        self.assertEqual(25, csvwrapper.mapIndex('z'));
        self.assertEqual(25, csvwrapper.mapIndex('25'));
        self.assertEqual(25, csvwrapper.mapIndex('csv:Z'));

        self.assertEqual(26, csvwrapper.mapIndex('AA'));
        self.assertEqual(26, csvwrapper.mapIndex('aa'));
        self.assertEqual(26, csvwrapper.mapIndex('26'));
        self.assertEqual(26, csvwrapper.mapIndex('csv:AA'));
        
        self.assertEqual(701, csvwrapper.mapIndex('ZZ'));
        self.assertEqual(701, csvwrapper.mapIndex('zz'));
        self.assertEqual(701, csvwrapper.mapIndex('701'));
        self.assertEqual(701, csvwrapper.mapIndex('csv:ZZ'));


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()