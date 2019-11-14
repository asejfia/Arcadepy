'''
Created on May 18, 2010

@author: joshuaga
'''

import sys, os, string, logging
import getopt, re
import config

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def printWalkData(root, dirs, files):
    logging.debug(str(root) + '\n')
    logging.debug(str(dirs) + '\n')
    logging.debug(str(files) + '\n')
    logging.debug('\n\n')
    
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def separateCamelCase(name):
    s1 = first_cap_re.sub(r'\1 \2', name)
    return all_cap_re.sub(r'\1 \2', s1).lower()
    
def splitWordsByCamelCase():
    innerClassSep = True
    
    config.get_config_from_filename()
    
    prefixOutput = config.subjectsDir
    
    #prefixInput = "/home/joshua/Documents/joshuaga-jpl-macbookpro/Documents/workspace"
    #prefixInput = "/home/joshua/Documents/joshuaga-jpl-macbookpro/Documents/workspace"
    prefixInput = config.subjectsDir;
    
    outputDir = ''
    if innerClassSep:
        outputDir = prefixOutput + os.sep + config.projectDirName + os.sep + 'cc_ics'
    else:
        outputDir = prefixOutput + os.sep + config.projectDirName + os.sep + 'camelcase_separated'
    logging.debug("outputDir: " + outputDir)
    startDir = prefixOutput + os.sep + config.projectDirName + os.sep + 'separated'
    logging.debug("startDir: " + startDir)
    
    javaKeywordFile = open('res' + os.sep + 'javakeywords','r')
    javaKeywords = []
    for line in javaKeywordFile:
        javaKeywords.append(line.strip())
        
    
    logging.debug("javaKeywords: " + str(javaKeywords))
    
    cppKeywordFile = open('res'+os.sep+'cppkeywords','r')
    cppKeywords = []
    for line in cppKeywordFile:
        cppKeywords.append(line.strip())
        
    logging.debug("cppKeywords: " + str(cppKeywords))
    
    cKeywordsFile = open('res'+os.sep+'ckeywords','r')
    cKeywords = []
    for line in cKeywordsFile:
        cKeywords.append(line.strip())
        
    logging.debug("cKeywords: " + str(cKeywords))
    
    #outputDir = "/Users/joshuaga/Documents/Software Engineering Research/Subjects/freecs/camelcase_separated"
    #startDir = "/Users/joshuaga/Documents/Software Engineering Research/Subjects/freecs/separated"
    dirlisting = os.listdir(startDir)
    logging.debug(str(dirlisting))
    
    expr = ""
    if config.langType == config.Langs.cpp:
        expr = ".cpp"
    elif config.langType == config.Langs.java:
        expr = ".java"
    elif config.langType == config.Langs.cfunc:
        expr = ".func"
    elif config.langType == config.Langs.cfile:
        expr = "(.h)|(.c)|(.S)|(.tbl)|(.p)|(.cpp)|(.cc)"
    
    for root, dirs, files in os.walk(startDir):
        printWalkData(root, dirs, files)
        
        for file in files:
            currdir, ext = os.path.splitext(file)
            if re.search(expr,ext):
                logging.debug("top-level class name and location: ")
                logging.debug(root + os.sep + file)
                #if (not (file == "LlamaChat.java") ):
                #    continue
                fd = open(root + os.sep + file,'r')
                
                if not os.path.exists(outputDir):
                    os.makedirs(outputDir)
                    
                relativePath = root.replace(startDir,"") + os.sep 
                absDirContainingFile = outputDir + os.sep + relativePath
                outFullFilename = absDirContainingFile + os.sep + file
                if not os.path.exists(absDirContainingFile):
                    os.makedirs(absDirContainingFile)
                outf = open(outFullFilename, 'w')
                
                
                for lineNo, line in enumerate(fd):
                    pattern = re.compile('[\W_]+')
                    alphanumericOnlyLine = pattern.sub(' ',line)
                    
                    splitLineList = alphanumericOnlyLine.split(' ')
                    removeList = []
                    logging.debug('splitLineList: ' + str(splitLineList))
                    for strSplit in splitLineList:
                        logging.debug('str in splitLineList: ' + strSplit)
                        strippedStr = strSplit.strip()
                        if config.langType == config.Langs.java:
                            for keyword in javaKeywords:
                                #print 'keyword: ', keyword
                                #print 'strippedStr: ', strippedStr
                                if keyword.lower() == strippedStr.lower():
                                    logging.debug('Adding ' + strSplit + ' to removeList')
                                    removeList.append(strSplit)
                        if config.langType == config.Langs.cpp:
                            for keyword in cppKeywords:
                                #print 'keyword: ', keyword
                                #print 'strippedStr: ', strippedStr
                                if keyword.lower() == strippedStr.lower():
                                    logging.debug('Adding ' + strSplit + ' to removeList')
                        if config.langType == config.Langs.cfunc or config.langType == config.Langs.cfile:
                            for keyword in cKeywords:
                                #print 'keyword: ', keyword
                                #print 'strippedStr: ', strippedStr
                                if keyword.lower() == strippedStr.lower():
                                    logging.debug('Adding ' + strSplit + ' to removeList')
                                    removeList.append(strSplit)
                    logging.debug('removeList: ' + str(removeList))
                    for strRemoved in removeList:
                        splitLineList = filter(lambda item : item.lower() != strRemoved.lower(),splitLineList)
                    logging.debug('line with keywords removed: ')
                    logging.debug(str(splitLineList))
                    
                    splitLine = ''
                    for i in range(len(splitLineList)):
                        strSplit = splitLineList[i]
                        splitLine = splitLine + strSplit
                        if i != (len(splitLineList) - 1 ):
                            splitLine = splitLine + ' '
                            
                    splitLine = splitLine

                    upperCount = 0      
                    lineToWrite = ''
                    LOWER, UPPER, NOTALPHA, UNINIT = range(4)
                    lastCharType = UNINIT       
                    for index, c in enumerate(splitLine):
                        if not re.search(r"[a-zA-Z]",c): # if not a letter
                            lineToWrite = lineToWrite + c
                            lastCharType = NOTALPHA
                        elif c.islower(): # current character is lowercase
                            if (upperCount > 2 and lastCharType == UPPER):
                                lineToWrite = lineToWrite[:len(lineToWrite)-1] + " " + lineToWrite[len(lineToWrite)-1:] + c
                            else:
                                lineToWrite = lineToWrite + c
                            lastCharType = LOWER
                            upperCount = 0
                        elif c.isupper(): # current character is uppercase
                            if (lastCharType == LOWER):
                                lineToWrite = lineToWrite + " "
                            lastCharType = UPPER
                            upperCount = upperCount + 1
                            lineToWrite = lineToWrite + c
                        else:
                            errorStr =  'Unexpected character ' + c + ' in ' + splitLine + '\n'
                            print errorStr
                            logging.error(errorStr)
                            sys.exit(1)
                    outf.write(lineToWrite)
                    
                            
                fd.close()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
            
            fsock = open(config.workspaceLoc + os.sep + 'PySourceSeparator'+ os.sep +'out.log','w')
            sys.stdout = fsock
                
            splitWordsByCamelCase()                    
                
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == '__main__':
    sys.exit(main())
