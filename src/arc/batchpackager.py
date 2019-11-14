'''
Created on Jul 24, 2014

@author: joshua
'''

import argparse, os
import packager

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--startdir', type=str, required=True)
    parser.add_argument('--pkgprefixes', type=str, nargs='+', required=True)
    args = vars(parser.parse_args())
    
    startdir = args['startdir']
    pkgprefixes = args['pkgprefixes']

    for root, dirs, files in os.walk(startdir):
        print "root: ", root
        for dir in dirs:
            print "\tdir: ", dir
        for file in files:
            if file.endswith("rsf"):
                print "\trsf file: ", file
                filenameTokens = file.split(".")
                filePrefix = filenameTokens[:-1]
                fileSuffix = filenameTokens[-1]
                packagerArgs = "--pkgprefixes " + ' '.join(pkgprefixes) + " --infile " + root + os.sep + file + " --outfile " + root + os.sep + '.'.join(filePrefix) + "_pkgs." + fileSuffix
                print packagerArgs
                packager.main(packagerArgs.split(' '))