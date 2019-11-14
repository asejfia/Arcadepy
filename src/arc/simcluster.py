'''
Created on Apr 1, 2013

@author: joshua
'''

import argparse
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
    parser.add_argument('--authfile', type=str, required=True)
    parser.add_argument('--csvfile',type=str,required=True)

    args = vars(parser.parse_args())
    
    csvfilename = args['csvfile']
    
    sourcefile = open(args['sourcefile'],'r')
    sourceclusters = buildclustersfromfile(sourcefile) 
        
    authfile = open(args['authfile'],'r')
    authclusters = buildclustersfromfile(authfile)
    
    simResults = []            
#     simResult = calcmatchingclusters(csvfilename, sourceclusters, authclusters, 0.001, 0.20)
#     simResults.append([0.001, 0.20, simResult])
#     
#     simResult = calcmatchingclusters(csvfilename, sourceclusters, authclusters, 0.20, 0.40)
#     simResults.append([0.20, 0.40, simResult])
#     
#     simResult = calcmatchingclusters(csvfilename, sourceclusters, authclusters, 0.40, 0.60)
#     simResults.append([0.40, 0.60, simResult])
#     
#     simResult = calcmatchingclusters(csvfilename, sourceclusters, authclusters, 0.60, 0.80)
#     simResults.append([0.60, 0.80, simResult])
#     
#     simResult = calcmatchingclusters(csvfilename, sourceclusters, authclusters, 0.80, 1.01)
#     simResults.append([0.80, 1.01, simResult])
    

    thresholds = [(0.4,0.6),(0.6,0.8),(0.8,1.00),(0.5,1.00)]
    for thresholdpair in thresholds:
        lthresh = thresholdpair[0]
        uthresh = thresholdpair[1]
        matchedClusterTriples = calcmatchingclustersold(sourceclusters, authclusters, lthresh, uthresh)
        
        results = outputSimClusters(csvfilename, sourceclusters, authclusters, lthresh, uthresh, matchedClusterTriples)
        simResults.append([lthresh, uthresh, results])
    
    words = csvfilename.split(".")
    csvSummaryFilename = words[0] + "_summary." + words[1] 
    csvSummaryFile = open(csvSummaryFilename,"w") 
    
    headerLine = "lthresh, uthresh, srcRatio, authRatio"
    print headerLine
    csvSummaryFile.write(headerLine + "\n")
    for lthresh, uthresh, simResult in simResults:
        threshStr = str(lthresh) + "," + str(uthresh) +","
        print threshStr,
        csvSummaryFile.write(threshStr) 
        srcRatio =  simResult[0]
        authRatio = simResult[1]
        ratioStr = str(srcRatio) + "," + str(authRatio) + ","
        print ratioStr,
        csvSummaryFile.write(ratioStr)
        print
        csvSummaryFile.write("\n")
    
    csvSummaryFile.write("\n")
    csvSummaryFile.close()
        
#    authClusterPairsDict = buildclusterpairs(authclusters)
#    srcClusterPairsDict = buildclusterpairs(sourceclusters)
#    
#    print 'built all cluster pairs'
#    
#    matchedAuthClusterPairsDict = defaultdict(set)
#    print len(authClusterPairsDict)
#    print len(srcClusterPairsDict)
    
    #for authCluster, authClusterPairs in authClusterPairsDict.iteritems():
        #matchedAuthClusterPairs = set()
        #for srcCluster, srcClusterPairs in srcClusterPairsDict.iteritems():
            #for authClusterPair in authClusterPairs:
                #for srcClusterPair in srcClusterPairs:
                    #pass
                    #if authClusterPair == srcClusterPair:
                    #    matchedAuthClusterPairs.add(authClusterPair)
        #matchedAuthClusterPairsDict[authCluster] = matchedAuthClusterPairs
    
    #print
    #print 'matched cluster pairs ratios:'
    #for authCluster, matchedClusterPairs in matchedAuthClusterPairsDict.iteritems():
    #    print authCluster, float(len(matchedClusterPairs))/float(len(authClusterPairsDict[authCluster]))
        
    

if __name__ == '__main__':
    main()