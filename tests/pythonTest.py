'''
Created on May 22, 2015

@author: lancer
'''
import unittest
from  datetime  import date, datetime;
from string import Template;
from re import match, search

class TestEdiData(unittest.TestCase):
    def testDateFormat(self):
        date=datetime.now()
        astr=date.strftime("%Y%m%d")
        print astr;
        date=datetime(2010, 05, 23)
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

    def testMatch(self):
        t = r'.*\${([\w\s%,\'"\$\{\}]*)\}[^#]*(#+)';
        s = "JMS${today, '%Y%m%d'}678###";
        self.assertIsNotNone(match(t, s));
        matchObj = match(t, s);
        self.assertEqual("today, '%Y%m%d'", matchObj.group(1))
        (funcname, fmt ) = matchObj.group(1).split(',');
        print funcname, format 
        fn = getattr(date , "today")
        a = fn();
        print "aaaaaa" , a;
        output = a.strftime(fmt.strip());
        print output;
        
    def testSearch(self):
        t = r'(\${.*})';
        s = "JMS${today, '%Y%m%d'}678###";
        print s.find(t);
        matchObj = search(t, s);
        self.assertEqual("${today, '%Y%m%d'}", matchObj.group(1))
        t2 = "(#+)"
        matchObj = search(t2, s);
        self.assertEqual("###", matchObj.group(1))
        
        
        t = 'jms %(today1) %(count)03d'
        v = {'count': 1, 'today1': '20150606'}
        print '****', t%v;
        print 'jms %(today1)s ,  jhgf  %(count)03d' % {'count': 1, 'today1':'00000'}

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testLanguage']
    unittest.main()