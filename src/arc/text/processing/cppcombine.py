'''
Created on Dec 13, 2010

@author: joshua
'''

import sys, os, getopt, re, shutil

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
            
            fsock = open('/home/joshua/Documents/joshuaga-jpl-macbookpro/Documents/workspace/PySourceSeparator/out.log','w')
            sys.stdout = fsock
            
            
            prefixOutput = "/home/joshua/Documents/Software Engineering Research/Subjects"
            projectDirName = "MIDAS_refactored";
            
            #prefixInput = "/home/joshua/Documents/joshuaga-jpl-macbookpro/Documents/workspace"
            prefixInput = "/home/joshua/Documents/Software Engineering Research/Subjects"
            
            outputdir = prefixOutput + '/' + projectDirName + '/' + 'combinedHppandCpp'
            print "outputDir: ", outputdir
            startDir = prefixInput + '/' + projectDirName + '/separated'
            print "startDir: ", startDir
            
            dirlisting = os.listdir(startDir)
            print dirlisting
            
            for root, dirs, files in os.walk(startDir):
                #printWalkData(root, dirs, files)
                for fileHpp in files:
                    currdir, ext = os.path.splitext(fileHpp)
                    print "currdir: ", currdir
                    print "ext: ", ext
                    if re.search(r".hpp",ext):
                        for fileCpp in files:
                            currdir2, ext2 = os.path.splitext(fileCpp)
                            if currdir2 == currdir and re.search(r".cpp",ext2):
                                fin = open(startDir + '/' + fileHpp,"r")
                                dataHpp = fin.read()
                                fin.close()
                                
                                os.remove(startDir + '/' + fileHpp)
                                
                                fin = open(startDir + '/' + fileCpp,"r")
                                dataCpp = fin.read()
                                fin.close()
                                
                                combinedData = dataHpp + dataCpp
                                
                                fout = open(startDir + '/' + fileCpp,"w")
                                fout.write(combinedData)
                                fout.close()
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())