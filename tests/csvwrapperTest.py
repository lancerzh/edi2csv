'''
Created on May 19, 2015

@author: lancer
'''
import unittest

import csvwrapper


class Test(unittest.TestCase):


    def testFieldReadAndSkip(self):
        inputLine = "48377,134150427P00024,1,250,173230,,,,1,$15.00,$10.00,RVC,SND,RVC - Reimbursement from objective validation of nationally accepted billing and coding guidelines\n"
        csvDb = csvwrapper.CsvDatabase(inputLine);  # test skip here
        csvDb.next();
        self.assertEqual('134150427P00024', csvDb.get_value('csv:b'))
        self.assertEqual('1', csvDb.get_value('csv:c'))
        self.assertEqual('$10.00', csvDb.get_value('csv:k'))
        self.assertEqual('RVC', csvDb.get_value('csv:l'))
        self.assertEqual('SND', csvDb.get_value('csv:m'))
        self.assertEqual('RVC - Reimbursement from objective validation of nationally accepted billing and coding guidelines', csvDb.get_value('csv:n'))
        
    def testSkipAndSpace(self):
        inputLine = """
        
        48377, 134150427P00024, 1, "aaa"\n
        """
        csvDb = csvwrapper.CsvDatabase(inputLine, 2);  # test skip here
        csvDb.next();
        self.assertEqual('48377', csvDb.get_value('csv:a'))
        self.assertEqual('134150427P00024', csvDb.get_value('csv:b'))
        self.assertEqual('1', csvDb.get_value('csv:c'))
        self.assertEqual('aaa', csvDb.get_value('csv:d'))
    
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