'''
Created on May 18, 2015

@author: lancer
'''
import unittest
from re import match, IGNORECASE;

import x12edi
import csv2edi


class Test(unittest.TestCase):


    def testMatch(self):
        reInsert = r'insert\s+([\'"]?\S+~[\'"]?)\s+after\s+(\S+)';
        self.assertIsNotNone(match(reInsert, "insert  'NTE*ADD*~' after LX/K3"))
        self.assertIsNotNone(match(reInsert, 'insert "NTE*ADD*~"  after LX/K3'))
        self.assertIsNotNone(match(reInsert, "insert  NTE*ADD*~  after  LX/K3"))
        self.assertIsNotNone(match(reInsert, "INSERT \t 'NTE*ADD*~' AFTER LX/K3", IGNORECASE))

        reSetvalue = r'setvalue\s+(\$\{csv:[\w]+\})\s+into (.+)'
        self.assertIsNotNone(match(reSetvalue, 'setvalue ${csv:k} into LX/HCP*02/02'));
        
        reAppend = r'append\s+(csv:[\w]+)\s+at\s+(.+)'
        self.assertIsNotNone(match(reAppend, 'append csv:m at LX/NTE*ADD/02,01'));
        
        reText = r'[\'"]?[^\$][\w]+[\'"]?'
        self.assertIsNotNone(match(reText, 'aStringText'));
        self.assertIsNotNone(match(reText, '"aStringText"'));
        self.assertIsNotNone(match(reText, "'aStringText'"));
        self.assertIsNone(match(reText, "'$aStringText'"));
        self.assertIsNone(match(reText, "'${aStringText}'"));
        
        reVar = r'[\'"]?\$\{[\w]+\}[\'"]?'
        self.assertIsNotNone(match(reVar, '${aVar}'));
        self.assertIsNotNone(match(reVar, '"${aVar}"'));
        self.assertIsNotNone(match(reVar, "'${aVar}'"));
        self.assertIsNone(match(reVar, "'aVar'"));
        self.assertIsNone(match(reVar, "'{aVar}'"));


        reCsv = r'[\'"]?\$\{csv:[\w]+\}[\'"]?'
        self.assertIsNotNone(match(reCsv, '${csv:k}'));
        self.assertIsNotNone(match(reCsv, '"${csv:k}"'));
        self.assertIsNotNone(match(reCsv, "'${csv:k}'"));
        self.assertIsNotNone(match(reCsv, '${csv:kk}'));
        self.assertIsNotNone(match(reCsv, '${csv:KK}'));
        self.assertIsNotNone(match(reCsv, '${csv:0}'));
        self.assertIsNotNone(match(reCsv, '${csv:10}'));

        pass
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()