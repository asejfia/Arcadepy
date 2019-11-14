#!/usr/bin/python

import argparse, platform, shlex, subprocess, os

cwdList = os.getcwd().split(os.sep)

parser = argparse.ArgumentParser(description='create topic model and associated output files')
parser.add_argument('--mallet',dest='mallet',help='location of mallet executable',default=os.environ['MALLET'])
parser.add_argument('--model',dest='model',help='name of the mallet model',default = cwdList[-1])
parser.add_argument('--start-range',dest='startrange',help='start range for number of topics',default=10)
parser.add_argument('--end-range',dest='endrange',help='end range for number of topics', default=10)
parser.add_argument('--range-step',dest='rangestep',help='step for range', default=10)
parser.add_argument('--num-iterations',dest='numiters',help='number of iterations to run sampling', default='1000')
parser.add_argument('--num-threads',dest='numthreads',help='number of threads to use', default='2')
args = parser.parse_args()

for numtopics in range(int(args.startrange),int(args.endrange)+int(args.rangestep),int(args.rangestep)):
  numTopicsStr = str(numtopics)
  print 'args: ', args
  command_line = args.mallet + ' train-topics --input ' + args.model + '.mallet --output-model ' + args.model + '-topic-model.gz --num-threads ' + args.numthreads + ' \
  --num-topics ' + numTopicsStr + ' --num-iterations ' + args.numiters +  ' --doc-topics-threshold 0.0 --optimize-interval 10 --num-top-words 15 \
  --word-topic-counts-file ' + args.model + '-' + numTopicsStr + '-word-topic-counts.txt \
   --output-doc-topics ' + args.model + '-' + numTopicsStr + '-doc-topics.txt --output-topic-keys ' + args.model + '-' + numTopicsStr + '-topic-keys.txt'

  print 'Executing command line: '
  print command_line

  if (platform.system() == 'Windows'):
    cl_args = shlex.split(command_line,posix=False)
  else:
    cl_args = shlex.split(command_line)

  p = subprocess.call(cl_args)

  print p
