'''
Created on May 18, 2015

@author: lancer
'''
from re import match;


__SEGMENT_TERMINATION__ = '~'
__ELEMENT_SEPARATOR__ = '*'
__SUBELEMENT_SEPARATOR__ = ':'
__REPETITION_SEPARATOR__ = '^'

__LINE_TAIL__ = '~\n'

# LOOP character: 'NAME':['HIERARCH', 'ID LOCATION']
__LOOP_DEFINITION__ = {'ISA':['0100', 'ISA/ISA/13'], 
                              'GS':['0300', 'GS/GS/06'], 
                              'ST':['0500', 'ST/ST/02'],
                              'HL':['2000', 'HL/HL/01'],
                              'CLM':['2300', 'CLM/REF*D9/02'],
                              'LX':['2400', 'LX/LX/01']
                              };

def createEdi(edidata):
    if edidata.find(__LINE_TAIL__) < 0:
        orgEdidata = edidata.replace(__SEGMENT_TERMINATION__, '~\n').splitlines();
    else :
        #orgEdidata = edidata.replace(__SEGMENT_TERMINATION__, '').splitlines();
        orgEdidata = edidata.splitlines();
    return EdiDoc(orgEdidata);




class EdiDoc :
    
    def __init__(self, edidata):
        self.isaNode = None;
        self.gsNode = None;
        self.transactions = [];

        self.orgEdidata = edidata;
        
        (self.isaNode, leftData) = self.unpackEnvelope(self.orgEdidata, 'ISA', 'IEA');
        
        (self.gsNode, leftData) = self.unpackEnvelope(leftData, 'GS', 'GE');
        self.gsNode.setParent(self.isaNode);
                
        self.sortingTransactions(leftData);
        
    def unpackEnvelope(self, data, headName, tailName):
        envelope = None;
        if data[0].startswith(headName) :
            envelope = EdiDocNode([data[0]]);
        else :
            print "err: not BEGIN with :", headName
            exit();
        if data[-1].startswith(tailName) :
            envelope.tail.append(data[-1])
        else :
            print "err: not END with :", tailName
            exit();             
        return (envelope, data[1:-1])
    
    def sortingTransactions(self, data):
        childrenData = [];
        index = 0;
        trans = None;
        currentTransactionData = [];
        while index < len(data) :
            seg = data[index];
            segName = seg.split(__ELEMENT_SEPARATOR__)[0];
            if segName == 'ST' :
                currentTransactionData.append(seg);
                index += 1;
                while True:
                    ''' read transaction itself's data. read until first sub loop line. '''
                    nextSeg = data[index];
                    firstElement = nextSeg.split(__ELEMENT_SEPARATOR__)[0]
                    if firstElement in __LOOP_DEFINITION__.keys() :
                        break;
                    else :
                        currentTransactionData.append(data[index]);
                        index += 1;
                trans = EdiDocNode(currentTransactionData, self.gsNode);
            elif segName == 'SE' :
                trans.tail += [seg];
                self.sortingLoops(childrenData, trans);    
                childrenData = [];
                currentTransactionData = []
                index += 1;
            else :
                childrenData.append(seg);
                index += 1;
    
    def sortingLoops(self, loopsData, transaction):
        loops = []
        currentLoopLines = [];
        lastLoop = transaction;
        for segment in loopsData:
            segName = segment.split(__ELEMENT_SEPARATOR__)[0];
            if segName in __LOOP_DEFINITION__.keys() :
                # see if loop is end 
                # if currentLoop has data and coming a new loop start flag
                # it is a new loop
                if len(currentLoopLines) > 0:
                    if len(loops) > 0 :
                        lastLoop = loops[-1];
                    else :
                        lastLoop = transaction;
                    parent = lastLoop.getParent(currentLoopLines[0]);
                    aLoop = EdiDocNode(currentLoopLines, parent);
                    loops.append(aLoop);
                    currentLoopLines = [];
                    
            currentLoopLines.append(segment);
        else :
            if len(loops) > 0 :
                lastLoop = loops[-1];
            else :
                lastLoop = transaction;
            parent = lastLoop.getParent(currentLoopLines[0]);
            aLoop = EdiDocNode(currentLoopLines, parent);
            loops.append(aLoop);
        return loops;
    

    def traverse(self):
        return self.isaNode.traverse();
    
    def fetchSubNodes(self, loopName):
        return self.isaNode.fetchSubNodes(loopName);
    

class EdiDocNode :

    def __init__(self, lines=[], parent=None):
        self.body = []
        self.tail = [];
        
        self.children = []
        self.deep = 0;
        self.setParent(parent);
        
        self.hierarch = HierarchLocator(lines[0]);
        self.name = self.hierarch.levelName;
        self.body = lines;
        self.id = self.getValue(__LOOP_DEFINITION__[self.name][1])

    def setParent(self, parent):
        self.parent = parent;
        if parent != None:
            parent.children.append(self);
            self.deep = parent.deep + 1;

    def getValue(self, location):
        l = ValueLocator(location);
        if l.hierarch == self.hierarch : 
            for seg in self.body :
                if seg.startswith(l.segmentPattern) :
                    try :
                        return l.getValue(seg);
                    except IndexError as ie:
                        ie.msg = self;
                        raise;
        elif self.parent == None :
            return '';
        else :
            return self.parent.getValue(location);
        
    def dump(self):
        segs = [];
        segs += self.body;
        for c in self.children :
            segs = segs + c.dump();
        segs += self.tail;
        return segs;
    
    def traverse(self):
        queue = [];
        queue.append(self);
        for node in self.children :
            queue += node.traverse();
        return queue
    
    def fetchSubNodes(self, loopName):
        locator =  HierarchLocator(loopName);
        queue = [];
        if locator == self.hierarch :
            queue.append(self);
            return queue;
        for node in self.children :
            queue += node.fetchSubNodes(loopName);
        return queue

    def getParent(self, loophead):
        locator =  HierarchLocator(loophead);
    
        if locator.level == __LOOP_DEFINITION__['ISA'][0] : #  loop '0100' :
            return None
        elif locator > self.hierarch :
            return self
        return self.parent.getParent(loophead)
    
    @property
    def header(self):
        return self.body[0];
        
class HierarchLocator:
    __SEPARATOR__ = ':';
    def __init__(self, locator):
        self.locator = locator;
        if locator.find(__ELEMENT_SEPARATOR__) > 0: # x12 edi loop line
            words = locator.split(__ELEMENT_SEPARATOR__);
            self.levelName = words[0];
            self.level = __LOOP_DEFINITION__[self.levelName][0];
            self.subLevel = None;
            if self.level == '2000':  # HL Hierarch Level 
                self.subLevel = words[03];
        elif locator.find(HierarchLocator.__SEPARATOR__) > 0: # hierarch definition
            words = locator.split(HierarchLocator.__SEPARATOR__);
            self.levelName = words[0];
            self.level = __LOOP_DEFINITION__[self.levelName][0];
            self.subLevel = words[1];
        else :
            self.levelName = locator;
            self.level = __LOOP_DEFINITION__[self.levelName][0];
            self.subLevel = None;

    
    def __cmp__(self,other):
        if self.level != other.level or self.subLevel is None or other.subLevel is None :
            return cmp(self.level, other.level);
        else :
            return cmp(self.subLevel, other.subLevel);

class ValueLocator:
    def __init__(self, location):
        (hn, lineHeader, position)  = location.split('/', 2);
        self.location = location;
        self.hierarch = HierarchLocator(hn);
        self.segmentPattern = lineHeader;
        
        matchObj = match(r'([0-9]+)([,:/]?)([0-9]*)' , position)
        (self.elementPos, self.subElePos, self.subEleSep) = (int(matchObj.group(1)), matchObj.group(3), matchObj.group(2));
        
    def getValue(self, segment):
        elements = segment.strip('~').split(__ELEMENT_SEPARATOR__);
        if not self.isSubElement() :
            return elements[self.elementPos];
        else :
            try :
                ''' sub elements maybe is empty
                '''
                subEles = elements[self.elementPos].split(self.subEleSep);
                return subEles[self.subElementPos - 1]
            except IndexError as ie:
                ie.msg = segment;
                raise;
            
    def isSubElement(self):
        return self.subElePos != '';
    
    @property
    def subElementPos(self):
        return int(self.subElePos) if self.isSubElement()  else None


    