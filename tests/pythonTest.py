'''
Created on May 22, 2015

@author: lancer
'''
import unittest
import datetime;
from string import Template;

class TestEdiData(unittest.TestCase):
    def testDateFormat(self):
        date=datetime.datetime.now()
        astr=date.strftime("%Y%m%d")
        print astr;
        date=datetime.datetime(2010, 05, 23)
        self.assertEqual('20100523', date.strftime("%Y%m%d"))
        
        
    def testStringTemplateSubstitute(self):
        template = Template('$a $b');
        d = {'a':'aaa', 'b':'bbbbb'}
        self.assertEqual('aaa bbbbb', template.substitute(d));
        template = Template('${a} ${b}');
        d = {'a':'AAA', 'b':'BBBBB', 'c':''}
        self.assertEqual('AAA BBBBB', template.substitute(d));
        
        template = Template('${a} ${b} ${cVar}, $d');
        d = {'a':'AAA', 'b':'BBBBB'}
        try:
            self.assertEqual('AAA BBBBB', template.substitute(d));
        except KeyError as e:
            print e, 'not present'
            pass

        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testLanguage']
    unittest.main()