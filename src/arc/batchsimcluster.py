#!/usr/local/bin/python2.7
# encoding: utf-8
'''
arc.batchsimcluster -- shortdesc

arc.batchsimcluster is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2014 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import simcluster

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-04-21'
__updated__ = '2014-04-21'

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

  Created by user_name on %s.
  Copyright 2014 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser() #(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('--startdir', type=str, required=True)
        parser.add_argument('--gtfile',type=str,required=True)
        parser.add_argument('--lthresh',type=float,default=0.66)
        parser.add_argument('--uthresh',type=float,default=1)

        # Process arguments
        args = vars(parser.parse_args())

        for root, dirs, files in os.walk(args['startdir']):
            print 'root, dirs: ', root, dirs
            print '\t', files
            sumc2c = float(0)
            c2clist = []
            countc2c = 0
            for file in files:
                if str(file).endswith(".rsf"):
                    srcfilename = os.path.join(str(root),str(file))
                    print '\t\t Running simcluster (c2c) for ' + srcfilename + ' against ' + args['gtfile'] + ' for threshold ' + str(args['lthresh']) + ' and ' + str(args['uthresh'])
                    c2c = simcluster.calc_c2c_new(srcfilename, args['gtfile'], args['lthresh'], args['uthresh'])
                    print '\t\t', c2c
                    sumc2c = sumc2c + c2c
                    countc2c = countc2c + 1
                    c2clist.append(c2c)
            if countc2c != 0:
                avgc2c = float(sumc2c)/float(countc2c)
                print '\t\tavg cvg:',avgc2c
                print '\t\tmax cvg: ',max(c2clist)
            #for file in files:
            #    if str(file).endswith(".rsf"):
            #        print os.path.dirname(file), file

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
        profile_filename = 'arc.batchsimcluster_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())