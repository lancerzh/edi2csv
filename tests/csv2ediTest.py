'''
Created on May 18, 2015

@author: lancer
'''
import unittest

import x12edi
import csv2edi


class Test(unittest.TestCase):


    def testName(self):
        config = 'csvwrapper.ini'
        csv = 'Test/JMS_RELIANT_I_20150505output.csv'
        in_edi = 'RHPPAI_0505151403_3.txt'
        out_edi = 'edi_out.txt'
        
        sb = csv2edi.proc(in_edi, csv, config);
        self.assertEqual('', sb)
        pass
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()