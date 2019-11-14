'''
Created on Mar 22, 2010

@author: joshuaga




'''

import sys, os, string
import getopt, re
import config
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def writeTopLevelClasses(fullFilename, clines, splitInitComments, piStmts):
    outf = open(fullFilename, 'w')
    for line in piStmts:
        outf.write(line)
    
    skipList = []
    for index, initComments in enumerate(splitInitComments):
        for line in initComments:
            if not string.lower(line).find("copyright") == -1:
                skipList.append(index)
    
    skipSet = set(skipList)
    for index, initComments in enumerate(splitInitComments):
        if not index in skipSet:
            for line in initComments:
                outf.write(line)
    
    for line in clines:
        outf.write(line)
        
def printTopLevelClasses(clines, initComments, piStmts):
    for line in piStmts:
        print line
    
    for line in initComments:
        print line
    
    for line in clines:
        print line

def writeNestedClasses(outputdir,nestedClassNames,nestedClasses, splitInitComments, piStmts, commentsList): 
    for index, c in enumerate(nestedClasses):
        print "Writing out nested class %s" % nestedClassNames[index]
        outf = open(outputdir + '/' + nestedClassNames[index] + '.java' ,'w')
        for line in piStmts:
            outf.write(line)
        
        skipList = []
        for icIndex, initComments in enumerate(splitInitComments):
            for line in initComments:
                if not string.lower(line).find("copyright") == -1:
                    skipList.append(icIndex)
        
        skipSet = set(skipList)
        for icIndex, initComments in enumerate(splitInitComments):
            if not icIndex in skipSet:
                for line in initComments:
                    outf.write(line)
        
        for line in commentsList[index]:
            outf.write(line)
        
        for line in c:
            outf.write(line)

def printNestedClasses(nestedClasses, initComments, piStmts, commentsList):
    for index, c in enumerate(nestedClasses):
        for line in piStmts:
            print line
        
        for line in initComments:
            print line
        
        for line in commentsList[index]:
            print line
        
        for line in c:
            print line
        
def printWalkData(root, dirs, files):
    print str(root) + '\n'
    print str(dirs) + '\n'
    print str(files) + '\n'
    print '\n\n'

class BalancedBraces:
    def __init__(self):
        self.braceCount=0
        self.foundFirstBrace=False
    def balanced_braces(self, s):
        for c in s:
            if c == '{':
                self.braceCount += 1
                self.foundFirstBrace=True
            if c == '}':
                self.braceCount -= 1
            if self.braceCount < 0:
                print s + ':' + ' Brace Count turned negative'
        return self.braceCount
    

def extractInnerClasses():
    prefixOutput = "/home/joshua/Documents/Software Engineering Research/Subjects"
    
    #prefixInput = "/home/joshua/Documents/joshuaga-jpl-macbookpro/Documents/workspace"
    #prefixInput = "/home/joshua/Documents/joshuaga-jpl-macbookpro/Documents/workspace"
    prefixInput = config.subjectsDir
    
    outputdir = prefixOutput + '/' + config.projectDirName + '/' + 'separated'
    print "outputDir: ", outputdir
    startdir = ""
    if config.projectDirName == "oodt-filemgr":
        startdir = prefixInput
    else:
        startdir = prefixInput + '/' + config.projectDirName
    print "startDir: ", startdir
    
    dirlisting = os.listdir(startdir)
    print dirlisting
    
    for root, dirs, files in os.walk(startdir):
        #printWalkData(root, dirs, files)
        for f in files:
            currdir, ext = os.path.splitext(f)
            if re.search(r".java",ext):
                print "top-level class name and location: "
                print root + '/' + f
                #if (not (f == "LlamaChat.java") ):
                #    continue
                fd = open(root + '/' + f,'r')
                count = 0
                clines = []
                inclines = []
                nestedClasses = []
                initComments = []
                splitInitComments = []
                otherComments = []
                piStmts = []
                commentsList = []
                nestedClassNames = []
                countingBraces=False
                countingNestedBraces=False
                gettingInitComments=False
                grabbingComments = False
                foundTopmostClass=False
                bb = BalancedBraces()
                inbb = BalancedBraces()
                for lineNo, line in enumerate(fd):
                    if re.search(r"\s*package\s+\w+",line): # grab package statements
                        piStmts.append(line)
                    if re.search(r"\s*import\s+\w+",line): # grab import statements
                        piStmts.append(line)
                    if re.search(r"/\*",line) and not re.search(r"\*/",line): #grab opening comments
                        if not foundTopmostClass:
                            gettingInitComments=True
                            initComments.append(line) 
                        else:
                            otherComments = []
                            otherComments.append(line)
                            grabbingComments = True
                        continue
                    elif re.search(r"\*/",line): # grab closing comments
                        if not foundTopmostClass:
                            gettingInitComments=False
                            initComments.append(line)
                            splitInitComments.append(initComments)
                            initComments = []
                        else:
                            otherComments.append(line)
                            grabbingComments = False
                        continue
                    elif gettingInitComments: # grab lines in between opening and closing comments
                        if not foundTopmostClass:
                            initComments.append(line)
                        continue
                    elif grabbingComments:
                        otherComments.append(line)
                        continue
                    #r"\s+(class|interface)\s+\w+.*\{"
                    if re.search(r"[(public|private)\s+(\w+\s)*]*(class|interface|enum)\s+\w+.*",line): # start grabbing class lines
                        foundTopmostClass=True # at any point that why see a class declaration we mark that we have found the topmost class
                        firstBraceFound=False
                        if countingBraces: # if you are already grabbing class lines, then you are seeing a nested class
                            print "\tFound nested class: " + str(line)
                            print "\totherComments is: " + str(otherComments)
                            
                            bcount = bb.balanced_braces(line) # still need to count braces
                            
                            linelist = string.split(line)
                            print "linelist: ", linelist
                            classindex = 0
                            if re.search(r"class",line):
                                classindex = linelist.index("class")
                            elif re.search(r"interface",line):
                                classindex = linelist.index("interface")
                            elif re.search(r"enum",line):
                                classindex = linelist.index("enum")
                            else:
                                raise TypeError("Invalid type when detecting line identifying class")
                            classname = linelist[classindex + 1]
                            print "\Added nested class %s to nestedClassNames " % classname
                            nestedClassNames.append(classname)
                            
                            
                            
                            commentsList.append(otherComments) # add comments that are right before this class

                            inclines.append(line)
                            countingNestedBraces=True
                            inbbcount = inbb.balanced_braces(line)
                            if inbbcount == 0: 
                                countingNestedBraces=False
                                nestedClasses.append(inclines)
                                inbb = BalancedBraces()
                                inclines = []
                        else:  
                            clines.append(line)
                            countingBraces=True
                            bcount = bb.balanced_braces(line)
                            print str(lineNo) + ": " + line 
                            print "bbcount: " + str(bcount)
                            print "bb.foundFirstBrace: " + str(bb.foundFirstBrace)
                            if bcount == 0 and bb.foundFirstBrace: 
                                countingBraces = False
                            print "\tFound class declaration starting: " + str(line)
                    else: # if I'm not seeing the first line of a class declaration
                        if countingBraces: # if I'm currently picking up lines through a class
                            bcount = bb.balanced_braces(line)
                            #print str(lineNo) + ": " + line 
                            #print "bbcount: " + str(bcount)
                            if bcount == 0:
                                countingBraces = False
                            if countingNestedBraces:
                                inclines.append(line)
                                inbbcount = inbb.balanced_braces(line)
                                if inbbcount == 0:
                                    countingNestedBraces=False
                                    nestedClasses.append(inclines)
                                    inbb = BalancedBraces()
                                    inclines = []
                            else:
                                clines.append(line)
                #print 'bcount: ' + str(bcount)
                #for line in initComments:
                #    print line
                #print "piStmts: " + str(piStmts)
                #print "initComments: " + str(initComments)
               
                print "top-level class: "
                #printTopLevelClasses(clines, initComments, piStmts)
                print root + '/' + f
                
                if not os.path.exists(outputdir):
                    os.makedirs(outputdir)
                fullFilename = outputdir + '/' + f   
                print "initComments: " + str(initComments)
                print "printing clines..."      
                for cline in clines:
                    print cline               
                writeTopLevelClasses(fullFilename,clines,splitInitComments,piStmts)
                
                if len(nestedClassNames) > 0:    
                    print "nestedClasses: "
                    #printNestedClasses(nestedClasses, initComments, piStmts, commentsList)
                    print "nestedClassNames: " + str(nestedClassNames)
                    writeNestedClasses(outputdir,nestedClassNames,nestedClasses, splitInitComments, piStmts, commentsList)
                #for n in nestedClassNames:
                #    print root + '/' + n 
    
    #os.chdir(startdir + '/src');
    #print os.listdir('.')


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
            
            fsock = open(config.workspaceLoc + '/PySourceSeparator/out.log','w')
            sys.stdout = fsock
            
            
            extractInnerClasses()
            
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
