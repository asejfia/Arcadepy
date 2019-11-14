'''
Created on Apr 1, 2013

@author: joshua
'''

import argparse, simcluster
from collections import defaultdict


def coverage(sourceclusters, targetclusters, matchedClusterTriples, srcortarget):
    if srcortarget:
        matched_srcclusters=set()
        for src,tgt,sim in matchedClusterTriples:
            matched_srcclusters.add(src)
        cvgval = float(len(matched_srcclusters))/float( len(sourceclusters) )
        return cvgval
    else:
        matched_tgtclusters=set()
        for src,tgt,sim in matchedClusterTriples:
            matched_tgtclusters.add(tgt)
        cvgval = float(len(matched_tgtclusters))/float(len(targetclusters))
        return cvgval

def buildclustersfromfacts(sourcefacts):
    sourceclusters = defaultdict(list)
    for fact in sourcefacts:
        if sourceclusters[fact[1]] == None:
            sourceclusters[fact[1]] = [fact[2]]
        else:
            sourceclusters[fact[1]].append(fact[2])
    
    return sourceclusters

def buildclusterpairs(clusters):
    clusterPairs = defaultdict(set)        
    for cluster, entities in clusters.iteritems():
        pairs = set()
        for entity1 in entities:
            for entity2 in entities:
                if entity1 != entity2:
                    pair = frozenset([entity1,entity2])
                    pairs.add(pair)
        clusterPairs[cluster] = pairs
    
    return clusterPairs




def outputSimClusters(csvfilename, sourceclusters, authclusters, lowerSimThreshold, upperSimThreshold, simClustersTriples):
    matchedSourceClusters = set()
    matchedAuthClusters = set()
    print 
    print 'lower sim threshold: ', lowerSimThreshold
    print 'upper sim threshold: ', upperSimThreshold
    print 'matched clusters: '
    for sourceCluster, authCluster, sim in simClustersTriples:
        print sourceCluster, authCluster, sim
        matchedSourceClusters.add(sourceCluster)
        matchedAuthClusters.add(authCluster)
    
    unmatchedSrcClusters = set(sourceclusters.keys()) - set(matchedSourceClusters)
    unmatchedAuthClusters = set(authclusters.keys()) - set(matchedAuthClusters)
    srcRatio = float(len(matchedSourceClusters)) / float(len(sourceclusters.keys()))
    tgtRatio = float(len(matchedAuthClusters)) / float(len(authclusters.keys()))
    print 
    print 'num of source clusters that match: ', len(matchedSourceClusters)
    print 'total num of source clusters: ', len(sourceclusters.keys())
    print 'ratio of matched source clusters: ', srcRatio
    print 
    print 'num of auth clusters that match: ', len(matchedAuthClusters)
    print 'total num of auth clusters: ', len(authclusters.keys())
    print 'ratio of matched auth clusters: ', tgtRatio
    print 'num unmatched src clusters: ', len(unmatchedSrcClusters)
    print 'unmatched src clusters:'
    for cluster in unmatchedSrcClusters:
        print cluster
    
    print 
    print 'num unmatched auth clusters: ', len(unmatchedAuthClusters)
    print 'unmatched auth clusters:'
    for cluster in unmatchedAuthClusters:
        print cluster
    
    print 
    words = csvfilename.split(".")
    newCsvFilename = words[0] + "_" + str(lowerSimThreshold) + "_" + str(upperSimThreshold) + "_combined." + words[1]
    csvfile = open(newCsvFilename, 'w')
    print 'csv format of auth cluster matching:'
    for cluster in authclusters:
        if cluster in unmatchedAuthClusters:
            missStr = '{0},{1}\n'.format(cluster, 'miss')
            print missStr
            csvfile.write(missStr)
        else:
            matchStr = '{0},{1}\n'.format(cluster, 'match')
            print matchStr
            csvfile.write(matchStr)
    
    csvfile.write('{0},{1}\n'.format("ratio of matched source clusters", srcRatio))
    csvfile.write('{0},{1}\n'.format("ratio of matched auth clusters", tgtRatio))
    csvfile.close()
    
    return srcRatio, tgtRatio

def calcmatchingclusters(sourceclusters, authclusters, lowerSimThreshold, upperSimThreshold):
    assert lowerSimThreshold >= 0, 'lowerSimThreshold < 0'
    assert upperSimThreshold <= 1, 'upperSimThreshold > 1'
    matchedClusterTriples = []
    for sourceCluster, sourceEntities in sourceclusters.iteritems():
        for authCluster, authEntities in authclusters.iteritems():
            sourceSet = set(sourceEntities)
            authSet = set(authEntities)
            inter = sourceSet & authSet
            #===================================================================
            # simDenom = float(len(sourceSet)+len(authSet)-2*len(inter))
            # sim = 1
            # if simDenom == 0:
            #     sim = 1
            # else:
            #     sim = float(len(inter)) / simDenom
            #===================================================================
            sim = float(len(inter)) / float(max( len(sourceSet),len(authSet) ))
            #sim = float(2*len(inter)) / float(len(sourceSet)+len(authSet))
            if sim > float(lowerSimThreshold) and sim <= float(upperSimThreshold):
                matchedClusterTriples.append((sourceCluster, authCluster, sim))
    
    return matchedClusterTriples

def calc_max_match_per_cluster(sourceclusters, authclusters, lowerSimThreshold, upperSimThreshold):
    assert lowerSimThreshold >= 0, 'lowerSimThreshold < 0'
    assert upperSimThreshold <= 1, 'upperSimThreshold > 1'
    maxSim = {}
    for sourceCluster, sourceEntities in sourceclusters.iteritems():
        max_sim_for_src = 0
        for authCluster, authEntities in authclusters.iteritems():
            sourceSet = set(sourceEntities)
            authSet = set(authEntities)
            inter = sourceSet & authSet
            #===================================================================
            # simDenom = float(len(sourceSet)+len(authSet)-2*len(inter))
            # sim = 1
            # if simDenom == 0:
            #     sim = 1
            # else:
            #     sim = float(len(inter)) / simDenom
            #===================================================================
            sim = float(len(inter)) / float(max( len(sourceSet),len(authSet) ))
            #sim = float(2*len(inter)) / float(len(sourceSet)+len(authSet))
            if sim > max_sim_for_src:
                maxSim[sourceCluster] = (authCluster,sim)
                max_sim_for_src = sim
    
    return maxSim

def calcmatchingclustersold(sourceclusters, authclusters, lowerSimThreshold, upperSimThreshold):
    assert lowerSimThreshold >= 0, 'lowerSimThreshold < 0'
    assert upperSimThreshold <= 1, 'upperSimThreshold > 1'
    matchedClusterTriples = []
    for sourceCluster, sourceEntities in sourceclusters.iteritems():
        for authCluster, authEntities in authclusters.iteritems():
            sourceSet = set(sourceEntities)
            authSet = set(authEntities)
            inter = sourceSet & authSet
            #===================================================================
            # simDenom = float(len(sourceSet)+len(authSet)-2*len(inter))
            # sim = 1
            # if simDenom == 0:
            #     sim = 1
            # else:
            #     sim = float(len(inter)) / simDenom
            #===================================================================
            sim = float(len(inter)) / float(len(sourceSet))
            #sim = float(2*len(inter)) / float(len(sourceSet)+len(authSet))
            if sim > float(lowerSimThreshold) and sim <= float(upperSimThreshold):
                matchedClusterTriples.append((sourceCluster, authCluster, sim))
    
    return matchedClusterTriples


def buildclustersfromfile(sourcefile):
    sourcefacts = []
    for line in sourcefile:
        fact = line.split()
        sourcefacts.append(fact)
    
    sourcefile.close()
    sourceclasses = set()
    for fact in sourcefacts:
        sourceclasses.add(fact[2])
    
    sourceclusters = buildclustersfromfacts(sourcefacts)
    return sourceclusters

def calc_c2c_old(sourcefilename,authfilename,lthresh,uthresh):
    
    sourcefile = open(sourcefilename,'r')
    sourceclusters = buildclustersfromfile(sourcefile) 
        
    authfile = open(authfilename,'r')
    authclusters = buildclustersfromfile(authfile)
    

    matchedClusterTriples = calcmatchingclustersold(sourceclusters, authclusters, lthresh, uthresh)
    
    matchedSourceClusters = set()
    matchedAuthClusters = set()
    for sourceCluster, authCluster, sim in matchedClusterTriples:
        #print sourceCluster, authCluster, sim
        matchedSourceClusters.add(sourceCluster)
        matchedAuthClusters.add(authCluster)
    
    #unmatchedSrcClusters = set(sourceclusters.keys()) - set(matchedSourceClusters)
    #unmatchedAuthClusters = set(authclusters.keys()) - set(matchedAuthClusters)
    #srcRatio = float(len(matchedSourceClusters)) / float(len(sourceclusters.keys()))
    tgtRatio = float(len(matchedAuthClusters)) / float(len(authclusters.keys()))
    return tgtRatio

def calc_c2c_new(sourcefilename,authfilename,lthresh,uthresh):
    
    sourcefile = open(sourcefilename,'r')
    sourceclusters = buildclustersfromfile(sourcefile) 
        
    authfile = open(authfilename,'r')
    authclusters = buildclustersfromfile(authfile)
    

    matchedClusterTriples = calcmatchingclusters(sourceclusters, authclusters, lthresh, uthresh)
    print 'matchedClusterTriples: ', matchedClusterTriples
    maxSim = calc_max_match_per_cluster(sourceclusters, authclusters, lthresh, uthresh)
    print 'non-zero max sim values for source and target clusters:'
    for key, value in maxSim.iteritems():
        print key, value
    
    matchedSourceClusters = set()
    matchedAuthClusters = set()
    for sourceCluster, authCluster, sim in matchedClusterTriples:
        print sourceCluster, authCluster, sim
        matchedSourceClusters.add(sourceCluster)
        matchedAuthClusters.add(authCluster)
    
    #unmatchedSrcClusters = set(sourceclusters.keys()) - set(matchedSourceClusters)
    #unmatchedAuthClusters = set(authclusters.keys()) - set(matchedAuthClusters)
    #srcRatio = float(len(matchedSourceClusters)) / float(len(sourceclusters.keys()))
    tgtRatio = float(len(matchedAuthClusters)) / float(len(authclusters.keys()))
    return tgtRatio

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sourcefile', type=str, required=True)
    parser.add_argument('--tgtfile', type=str, required=True)

    args = vars(parser.parse_args())
    
    sourcefile = open(args['sourcefile'],'r')
    sourceclusters = buildclustersfromfile(sourcefile) 
        
    tgtfile = open(args['tgtfile'],'r')
    tgtclusters = buildclustersfromfile(tgtfile)
    
    matched_cluster_triples = simcluster.calcmatchingclusters(sourceclusters, tgtclusters, 0.66, 1)
    srccvg = simcluster.coverage(sourceclusters, tgtclusters, matched_cluster_triples, True)  # calc coverage for source clusters
    tgtcvg = simcluster.coverage(sourceclusters, tgtclusters, matched_cluster_triples, False)  # calc coverage for source clusters
    print ' source coverage of source clusters from {0} to {1}: {2}'.format(str(sourcefile), str(tgtfile), srccvg)
    print ' target coverage of source clusters from {0} to {1}: {2}'.format(str(sourcefile), str(tgtfile), tgtcvg)
        
    

if __name__ == '__main__':
    main()
