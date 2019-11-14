'''
Created on Dec 13, 2010

@author: joshua
'''

import sys, os, getopt, re, shutil, config #@UnresolvedImport


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
        
def moveJavaFilesToSingleDir():
    prefixOutput = config.subjectsDir
    
    
    prefixInput = config.workspaceLoc;
    
    outputdir = prefixOutput + '/' + config.projectDirName + '/' + 'separated'
    print "outputDir: ", outputdir
    startdir = prefixInput + '/' + config.projectDirName
    print "startDir: ", startdir
    
    dirlisting = os.listdir(startdir)
    print dirlisting
    
    for root, dirs, files in os.walk(startdir):
        #printWalkData(root, dirs, files)
        for f in files:
            currdir, ext = os.path.splitext(f)
            print "currdir: ", currdir
            print "ext: ", ext
            
            regExp = ''
            
            if config.langType == config.Langs.java:
                regExp = '.java'
            elif config.langType == config.Langs.cpp:
                regExp = '[.cpp|.hpp]' 
            
            if re.search(r"" + regExp + "",ext):
                srcName = root + '/' + f
                dstName = outputdir + '/' + f 
                print "top-level class name and location: "
                print 'srcName: ' + srcName
                print 'dstName: ' + dstName
                if not os.path.exists(root):
                    os.makedirs(root)
                if not os.path.exists(outputdir):
                    os.makedirs(outputdir)
                shutil.copyfile(root + '/' + f, dstName)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
                       
            fsock = open(config.workspaceLoc + '/PySourceSeparator/out.log','w')
            sys.stdout = fsock
            
            moveJavaFilesToSingleDir()
            
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())