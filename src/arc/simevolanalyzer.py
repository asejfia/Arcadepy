#!/usr/local/bin/python2.7
# encoding: utf-8
'''
arc.simevolanalyzer -- perform c2c analysis over multiple versions or revisions of architectures

arc.simevolanalyzer is a tool that allows c2c analysis over multiple versions or revisions of architectures

It defines classes_and_methods

@author:     joshuaga

@copyright:  2014 USC. All rights reserved.

@license:    TBD

@contact:    joshuaga@usc.edu
@deffield    updated: Updated
'''

import sys
import os
import re
from os import listdir
from os.path import isfile, join, expanduser
import simcluster

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-02-17'
__updated__ = '2014-02-17'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
def convertStrToInt(s):
    """Convert string to int."""
    try:
        ret = int(s)
    except ValueError:
        return ret
    return ret
    
def compare(version1,version2):
    parts1 = version1.split(".");
    parts2 = version2.split(".");
    
    smallerparts = parts1 if len(parts1) < len(parts2) else parts2
    #print parts1
    #print parts2
    
    for idx, val in enumerate(smallerparts):
        cmpval = cmp(convertStrToInt(parts1[idx]),convertStrToInt(parts2[idx]))
        if cmpval != 0:
            return cmpval
    
    return cmp(version1,version2)


def runAnalysis(args, sortedfilesbyversion):
    for srcidx, (srcversion, srcfile) in enumerate(sortedfilesbyversion):
        for tgtidx in xrange(srcidx + 1, len(sortedfilesbyversion)):
            tgtversion = sortedfilesbyversion[tgtidx][0]
            tgtfile = sortedfilesbyversion[tgtidx][1]
            srcf = open(os.path.join(expanduser(args.inputdir), srcfile), 'r')
            tgtf = open(os.path.join(expanduser(args.inputdir), tgtfile), 'r')
            srcclusters = simcluster.buildclustersfromfile(srcf)
            tgtclusters = simcluster.buildclustersfromfile(tgtf)
            matched_cluster_triples = simcluster.calcmatchingclusters(srcclusters, tgtclusters, 0.66, 1)
            srccvg = simcluster.coverage(srcclusters, tgtclusters, matched_cluster_triples, True) # calc coverage for source clusters
            tgtcvg = simcluster.coverage(srcclusters, tgtclusters, matched_cluster_triples, False) # calc coverage for source clusters
            print ' source coverage of source clusters from {0} to {1}: {2}'.format(srcversion, sortedfilesbyversion[tgtidx][0], srccvg)
            print ' target coverage of source clusters from {0} to {1}: {2}'.format(srcversion, sortedfilesbyversion[tgtidx][0], tgtcvg)
        
        print '\n'

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by joshuaga on %s.
  Copyright 2014 USC. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('--inputdir',required=True)
        

        # Process arguments
        args = parser.parse_args()
        
        print args.inputdir

        onlyfiles = [ f for f in listdir(expanduser(args.inputdir)) if isfile(os.path.join(expanduser(args.inputdir),f)) ]
        filesbyversion = {}
        for f in onlyfiles:
            m = re.search("[0-9]+\.[0-9]+(\.[0-9]+)*", str(f))
            if m:
                found = m.group(0)
                #print found
                filesbyversion[found] = f
        
        sortedfilesbyversion = sorted(filesbyversion.items(),cmp = lambda e1,e2: compare(e1[0],e2[0]))
        print '\n'.join(map(str,sortedfilesbyversion))
        
        runAnalysis(args, sortedfilesbyversion)
        
        '''print filesbyversion
        for version, file in filesbyversion.items():
            print '{0} : {1}'.format(version,file)'''

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'arc.simevolanalyzer_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())