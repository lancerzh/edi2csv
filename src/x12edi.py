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
                              
__ELEMENT_MIN_MAX_LENGTH__ = {'ISA':['ISA', (2,2), (10,10), (2,2), (10,10), (2,2), (15,15), (2,2), (15,15), (6,6), (4,4), (1,1), (5,5), (9,9), (1,1), (1,1), (1,1)],
                              'NTE':['NTE', (3,3), (1,80)]
                              }

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
                    hierarch = HierarchLocator(currentLoopLines[0])
                    if hierarch > lastLoop.hierarch:
                        parent = lastLoop;
                    else :
                        parent = lastLoop.getParent(currentLoopLines[0]).parent;
                    #parent = lastLoop.getParent(currentLoopLines[0]);
                    aLoop = EdiDocNode(currentLoopLines, parent);
                    loops.append(aLoop);
                    currentLoopLines = [];
                    
            currentLoopLines.append(segment);
        else :
            if len(loops) > 0 :
                lastLoop = loops[-1];
            else :
                lastLoop = transaction;
            hierarch = HierarchLocator(currentLoopLines[0])
            if hierarch > lastLoop.hierarch:
                parent = lastLoop;
            else :
                parent = lastLoop.getParent(currentLoopLines[0]).parent;
            #parent = lastLoop.getParent(currentLoopLines[0]);
            aLoop = EdiDocNode(currentLoopLines, parent);
            loops.append(aLoop);
        return loops;
    

    def traverse(self):
        return self.isaNode.traverse();
    
    def fetchSubNodes(self, loopName):
        return self.isaNode.fetchSubNodes(loopName);
    

class EdiDocNode :
    ''' This class present a document node
    '''

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
                    except IndexError:
                        raise ElementNotFoundException(location, self, 'Not Found Element');
            else :
                raise ElementNotFoundException(location, self, 'Not Found Segment');
        elif l.hierarch < self.hierarch:
            return self.parent.getValue(location);
        else : # l.hierarch > self.hierarch 
            raise ElementNotFoundException(location, self, 'Not Found Loop');
        
    def setValue(self, value, location, method='REPLACE'):
        l = ValueLocator(location);
        if l.hierarch == self.hierarch : 
            for (i, seg) in enumerate(self.body):
                if seg.startswith(l.segmentPattern) :
                    self.body[i] = l.setValue(value, seg, method);
                    return;
        elif self.parent == None :
            raise IndexError;
        else :
            return self.parent.setValue(value, location);
        
        
    def replaceValue(self, value, location):
        return self.setValue(value, location, 'REPLACE');
    
    def appendValue(self, value, location):
        return self.setValue(value, location, 'APPEND');
        
    def dump(self):
        segs = [];
        segs += self.body;
        for c in self.children :
            segs = segs + c.dump();
        segs += self.tail;
        return segs;
        
    def __str__(self):
        output = '';
        for l in self.body :
            output += '  ' * self.deep + l + '\n';
        if len(self.children) > 0 :
            for c in self.children:
                output += c.__str__();
        if len(self.tail) > 0 :
            for l in self.tail :
                output += '  ' * self.deep + l;
        return output
        
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
    
        if locator >= self.hierarch :
            return self
        return self.parent.getParent(loophead)
    
    def insert(self, segment, position, order = 'AFTER'):
        length = len(self.body);
        for (i, line) in enumerate(reversed(self.body)):
            if line.startswith(position.upper()):
                self.body.insert(length - i, segment)
                break;

    @property
    def header(self):
        return self.body[0];
        
class HierarchLocator:
    ''' This class proc Loop hierarch description such as 'HL:20/', 'CLM/'
    '''
    __SEPARATOR__ = ':';
    def __init__(self, locator):
        locator = locator.upper();
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
    ''' this class proc value location description such like 'CLM/HCP/03-03'
    '''
    def __init__(self, location):
        self.location = location;
        (hn, lineHeader, position)  = self.location.upper().split('/', 2);
        self.hierarch = HierarchLocator(hn);
        self.segmentPattern = lineHeader;
        
        matchObj = match(r'([0-9]+)([,:/-]?)([0-9]*)' , position)
        (self.elementPos, self.subElePos, self.subEleSep) = (int(matchObj.group(1)), matchObj.group(3), matchObj.group(2));
        
    def getValue(self, segment):
        elements = segment.strip('~').split(__ELEMENT_SEPARATOR__);
        try :
            ''' element and sub elements maybe is empty
            '''
            if not self.hasSubElement() :
                return elements[self.elementPos];
            else :
                subEles = elements[self.elementPos].split(self.subEleSep);
                return subEles[self.subElementPos - 1]
        except IndexError:
            raise ;            
    def setValue(self, value, segment, method = 'REPLACE', sep = ','):
        words = segment.strip(__SEGMENT_TERMINATION__).split(__ELEMENT_SEPARATOR__);
        if method == 'APPEND':
            if value != None and len(value) > 0:
                words[self.elementPos] += sep +value;
        else :  #  default method == 'REPLACE':
            if not self.hasSubElement() :
                words[self.elementPos] = value;
            else :
                subEles = words[self.elementPos].split(self.subEleSep);
                subEles[self.subElementPos - 1] = value;
                words[self.elementPos] = self.subEleSep.join(subEles);
                        
        # check element has length limit
        if __ELEMENT_MIN_MAX_LENGTH__.get(words[0]) != None:
            vLength = len(words[self.elementPos])
            (mn, mx) =__ELEMENT_MIN_MAX_LENGTH__.get(words[0])[self.elementPos]
            if vLength > mx :
                print 'warning: it is over the element limit:' + str(mx)
                print words[self.elementPos]
                print 'Over limit chars will be cut out.'
                words[self.elementPos] = words[self.elementPos][:mx];
            if vLength < mn:
                words[self.elementPos] = words[self.elementPos] + ' ' * (mn - len(value))
        return __ELEMENT_SEPARATOR__.join(words) + __SEGMENT_TERMINATION__


    def hasSubElement(self):
        return self.subElePos != '';
    
    @property
    def subElementPos(self):
        return int(self.subElePos) if self.hasSubElement()  else None


class ElementNotFoundException(Exception):
    def __init__(self, locator, node, msg):
        Exception.__init__(self);
        self.locator = locator;
        self.docNode = node;
        self.msg = msg;
    def __str__(self):
        return self.msg + " '" + self.locator + "' in: \n" + self.docNode.__str__()
