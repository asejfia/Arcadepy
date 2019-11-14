'''
Created on Apr 3, 2013

@author: joshua
'''

import zclusterer
import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict
import logging

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sys', type=str, required=True)
    parser.add_argument('--srcml', type=str, required=True)
    parser.add_argument('--authfile', type=str, required=True)
    parser.add_argument('--outfile',type=str,default='outfile.csv')
    parser.add_argument('--weights', type=str, choices=['uni', 'em'], default='uni')
    parser.add_argument('--lang', type=str, choices=['java', 'c'], default='java')
    args = vars(parser.parse_args())
    
    #EASYMOCK_NAME = 'easymock'
    #JUNIT_NAME = 'junit'
    #JHOTDRAW_NAME = 'jhotdraw'
    
    sysname = args['sys']
    
    #junitFilename = '/home/joshua/Documents/source/junit4.5/junit4.5.xml'
    #easymockFilename = '/home/joshua/Documents/source/easymock2.4/src/easymock2.4.xml'
    
    #jhotdrawFilename = '/home/joshua/Documents/source/JHotDraw 7.4.1/Source/jhotdraw7/src/main/jhotdraw7.4.1.xml'
    selectedFilename = args['srcml']
    
    tree = ET.parse(selectedFilename)
    #root = tree.getroot()
    
    return args, sysname, tree

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    args, sysname, tree = setup()
    filenames, numDocs, sim = zclusterer.exec_first_phase(args,sysname,tree)
    
    authfile = open(args['authfile'],'r')
    
    clusters = defaultdict(list)
    for line in authfile:
        fact = line.split()
        if clusters[fact[1]] == None:
            clusters[fact[1]] = [fact[2]]
        else:
            clusters[fact[1]].append(fact[2])
    authfile.close()
            
    allEntities = set()
    for entities in clusters.itervalues():
        allEntities = allEntities | set(entities)
    
    foundEntities = set()
    clusterindices = defaultdict(list)
    print
    print 'clusters...'
    for cluster, entities in clusters.iteritems():
        for entity in entities:
            for fnIndex, filename in enumerate(filenames):
                convfilename = filename
                if args['lang'] == 'java':
                    convfilename = filename.replace('/','.')
                    convfilename = rreplace(convfilename,'.java','',1)
                if convfilename == entity:
                    print 'found: ', convfilename
                    foundEntities.add(entity)
                    if clusterindices[cluster] == None:
                        clusterindices[cluster] = [fnIndex]
                    else:
                        clusterindices[cluster].append(fnIndex) 
                        
    print 'cluster indices length: ', len(clusterindices)
    
    missingEntities = allEntities - foundEntities

    print
    print 'missing entities...'
    for entity in missingEntities:
        print entity
        
    print
    print 'entity indices for each cluster...'
    for cluster, indices in clusterindices.iteritems():
        print cluster, indices
        
    clusterSimVals = defaultdict(list)
    for cluster, indices in clusterindices.iteritems():
        sumOfMsrs = 0
        countOfMsrs = 0
        usedPairs = set()
        logging.debug('computing cluster')
        for i1 in xrange(0,len(indices),1):
            for i2 in xrange(i1+1,len(indices),1):
                index1 = indices[i1]
                index2 = indices[i2]
                pair = (index1,index2)
                if (index1 != index2) and (pair not in usedPairs):
                    logging.debug("cluster: {0}".format(cluster))
                    logging.debug("indices (1 then 2): {0} {1}".format(index1,index2))
                    logging.debug("sim: {0}".format(sim[index1][index2]))
                    sumOfMsrs = sumOfMsrs + sim[index1][index2]
                    countOfMsrs = countOfMsrs + 1
                    logging.debug("new sum: {0}".format(sumOfMsrs))
                    logging.debug("new count: {0}".format(countOfMsrs))
                    usedPairs.add(pair)
        
        clusterSimVal = 0
        if countOfMsrs == 0:
            clusterSimVal = 0
        else:
            clusterSimVal = sumOfMsrs/countOfMsrs
        logging.debug("final sim val for cluster: {0}".format(clusterSimVal))
        clusterSimVals[cluster] = clusterSimVal
        
    print
    print 'sim val for each cluster...'
    outf = open(args['outfile'],'w')
    for cluster, val in clusterSimVals.iteritems():
        print cluster, val
        outf.write('{0},{1}\n'.format(cluster,val))
    outf.close()
        
    

if __name__ == '__main__':
    main()