'''
Created on May 18, 2015

@author: lancer
'''



__LOOP_START_FLAGS__ = set(['ST', 'HL', 'CLM', 'LX']);
__LOOP_NAME__ = set(['HL', 'CLM', 'LX']);
__LOOP_END_FLAGS__ = set(['SE']);

__SEGMENT_TERMINATION__ = '~'
__ELEMENT_SEPARATOR__ = '*'
__SUBELEMENT_SEPARATOR__ = ':'
__REPETITION_SEPARATOR__ = '^'

__LINE_TAIL__ = '~\n'

__LOOP_FLAGS__ = set(['ST', 'HL', 'CLM', 'LX']);

# LOOP character: 'NAME':['HIERARCH', 'ID LOCATION']
__LOOP_HIERARCHICAL_DICT__ = {'ISA':['0100', 'ISA/ISA/13'], 
                              'GS':['0300', 'GS/GS/06'], 
                              'ST':['0500', 'ST/ST/02'],
                              'HL':['2000', 'HL/HL/01'],
                              'CLM':['2300', 'CLM/REF*D9/02'],
                              'LX':['2400', 'LX/LX/01']
                              };
'''
__LOOP_HIERARCHICAL_DICT__ = {'ISA':'0100', 
                              'GS':'0300', 
                              'ST':'0500', 
                              'HL':'2000', 
                              'CLM':'2300', 
                              'LX':'2400'};
'''
def createEdi(edidata):
    if edidata.find(__LINE_TAIL__) < 0:
        orgEdidata = edidata.replace(__SEGMENT_TERMINATION__, '\n').splitlines();
    else :
        orgEdidata = edidata.replace(__SEGMENT_TERMINATION__, '').splitlines();
    return EdiDoc(orgEdidata);


def getHierarch(name):
    return __LOOP_HIERARCHICAL_DICT__[name][0];

def getIdLocation(name):
    return __LOOP_HIERARCHICAL_DICT__[name][1];


    

class EdiDoc :
    
    def __init__(self, edidata):
        self.isaNode = None;
        self.gsNode = None;
        self.orgEdidata = [];
        self.transactions = [];

        self.orgEdidata = edidata;
        
        (self.isaNode, leftData) = self.unpackEnvelope(self.orgEdidata, 'ISA', 'IEA', None);
        
        (self.gsNode, leftData) = self.unpackEnvelope(leftData, 'GS', 'GE', self.isaNode);
                
        self.sortingTransactions(leftData);
        

    def unpackEnvelope(self, data, headName, tailName, parent = None):
        envelope = None;
        if data[0].startswith(headName) :
            envelope = EdiDocNode([data[0]], parent);
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
                    nextSeg = data[index];
                    firstElement = nextSeg.split(__ELEMENT_SEPARATOR__)[0]
                    if firstElement in __LOOP_START_FLAGS__ :
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
            if segName in __LOOP_FLAGS__ :
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
    

    
    
    def getMatched(self, conditions):
        
        for (segPattern, value) in conditions:
            print segPattern, ":", value;
            
        # no need here
        for loop in self.allLoops :
            if loop.name == segPattern and loop.isMatch(conditions) :
                return loop;
        print "err: not found matched loop"
        return EdiDocNode();

    def traverse(self):
        return self.isaNode.traverse();
    
    def getLoops(self, loopName, subHierach = '00'):
        return self.isaNode.getLoops(loopName, subHierach);
    

class EdiDocNode :

    def __init__(self, lines=[], parent=None):
        self.name = None
        self.hierarchical = None;
        self.hlCode = '00'
        
        self.children = []
        self.parent = parent;
        
        self.id = 'NO_ID';
        self.body = []
        self.tail = [];
        
        self.deep = 0;

        if parent :
            parent.children.append(self);
            self.deep = parent.deep + 1;
        if len(lines) > 0 :
            elements = lines[0].split(__ELEMENT_SEPARATOR__);
            self.name = elements[0];
            self.hierarchical = getHierarch(self.name);
            if self.name == 'HL' :
                self.hlCode = elements[3];
            self.body = lines;
            self.id = self.getValue(getIdLocation(self.name))

        pass;
    

    def getValue(self, location):
        [hn, lineHeader, position]  = location.split('/');
        hierarchs = hn.split(':');
        elementPos = int(position.split('-')[0])
        
        if hierarchs[0] == self.name : # TODO HL condition   or (len(hierarchs) == 2 and hierarchs[1] == self.hlCode) :
            for seg in self.body :
                if seg.startswith(lineHeader) :
                    elements = seg.split(__ELEMENT_SEPARATOR__);
                    if elementPos < len(elements):
                        return elements[elementPos];
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
    
    def isMatch(self, conditions):
        #CLM/REF*D9/02 = csv:b             
        #LX/LX/01 = csv:c

        for (pattern, value) in conditions:
            pattern = pattern.upper();
            [patternName, segHeader, elementPos]  = pattern.split('/');
            if patternName == self.name :
                for l in self.body :
                    elements = l.split(__ELEMENT_SEPARATOR__);
                    if l.startswith(segHeader) and elements[int(elementPos)] == value :
                        print l;
                        print value;
                        return True;
        return False;
    
    def traverse(self):
        queue = [];
        queue.append(self);
        for node in self.children :
            queue += node.traverse();
        return queue


    def isMyHierarch(self, loopName, subHierach='00'):
        return loopName == self.name and (loopName != 'HL' or subHierach == self.hlCode);

    def getLoops(self, loopName, subHierach = '00'):
        queue = [];
        if self.isMyHierarch(loopName, subHierach) :
            queue.append(self);
            return queue;
        for node in self.children :
            queue += node.getLoops(loopName, subHierach);
        return queue

    def getParent(self, loophead):
        elements = loophead.split(__ELEMENT_SEPARATOR__);
        name = elements[0];
        hlCode = '00';
        if name == 'HL' :
            hlCode = elements[03];
        hierarchical = getHierarch(name);
    
        if name == 'ISA' :
            return None
        elif hierarchical > self.hierarchical or (hierarchical == self.hierarchical and hlCode > self.hlCode) :
            return self
        return self.parent.getParent(loophead)
    
    @property
    def header(self):
        return self.body[0];
        
