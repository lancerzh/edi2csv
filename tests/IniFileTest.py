'''
Created on May 18, 2015

@author: lancer
'''
import unittest
import ConfigParser
import os


class Test(unittest.TestCase):


    def testFromFile(self):
        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read('from_reliant_csv.ini');
        for section in config.sections():
            print section
            for item in config.items(section):
                print item

        pass

    def testToFile(self):
        config = ConfigParser.RawConfigParser()
        config.optionxform = str

        config.read('to_reliant_csv.ini');
        for section in config.sections():
            print section
            for item in config.items(section):
                print item

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()