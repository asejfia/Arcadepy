'''
Created on Jun 9, 2011

@author: joshua
'''

import sys, os, getopt, re, shutil, config, subprocess, argparse, logging
import mvtosingle, class_sep, camelcase_sep, java_class_sep, stemmer


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    logging.basicConfig(filename='out.log',filemode='w',level=logging.ERROR)

    parser = argparse.ArgumentParser(description='pre-process java files for mallet')
    parser.add_argument('--configfile',dest='configfile',help='configuration filename',required=True)
    args = parser.parse_args()
    
    logging.debug('args.configfile: ' + args.configfile)
    config.configFilename = args.configfile
    
    config.get_config_from_filename()
               
    #fsock = open('out.log','w')
    #sys.stdout = fsock
    
    '''mvtosingle.moveJavaFilesToSingleDir()
    class_sep.extractInnerClasses()'''
    '''if config.langType == config.Langs.java:
        print 'Running java class separator...'
        java_class_sep.runClassSeparator()'''
        
    print 'Performing camel case splitting...'
    camelcase_sep.splitWordsByCamelCase()
    
    print 'Stemming...'
    stemmer.runStemmerOnDir()
    
    print 'Exiting'


if __name__ == "__main__":
    sys.exit(main())
