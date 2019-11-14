#! /usr/bin/python

import argparse, platform, shlex, subprocess, os

cwdList = os.getcwd().split(os.sep)

parser = argparse.ArgumentParser(description='create mallet model used for creating topic model')
parser.add_argument('--mallet',dest='mallet',help='location of mallet executable',default=os.environ['MALLET'])
parser.add_argument('--inputdir',dest='inputdir',help='directory that contains the java files that will be processed to create the mallet model',default='ccs_stemmed')
parser.add_argument('--model',dest='model',help='name of the mallet model',default=cwdList[-1])
args = parser.parse_args()

command_line = args.mallet + ' import-dir --input ' + args.inputdir + ' --output ' + args.model + '.mallet --keep-sequence --remove-stopwords'

print 'Executing command line: '
print command_line

if (platform.system() == 'Windows'):
    args = shlex.split(command_line,posix=False)
else:
    args = shlex.split(command_line)

p = subprocess.call(args)

print p
