'''
Created on Mar 18, 2013

@author: joshua

'''

import xml.etree.ElementTree as ET
import re
import camelcase_sep
import stemming.porter2
import Stemmer

from gensim import corpora, models, similarities
import numpy as np
import scipy.spatial.distance
from sklearn import mixture
import math

from functools import wraps
from time import time

import pickle, os, copy, string, argparse, cProfile, logging, sys

import pypr.clustering.gmm as gmm
from guppy import hpy

def timed(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    start = time()
    result = f(*args, **kwds)
    elapsed = time() - start
    print "%s took %d seconds to finish" % (f.__name__, elapsed)
    return result
  return wrapper

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sys', type=str, required=True)
    parser.add_argument('--srcml', type=str, required=True)
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

def get_all_text(elem):
    text = ''
    #if not elem.text == None:
    #    text = text + ' ' + elem.text
    if elem.tag == 'comment':
        print 'get_all_text was passed a comment tag'
        return text
    for child in elem:
        if child.tag == 'comment':
            continue
        if child.text == None:
            pass
        else:
            text = text + ' ' + child.text
        text = text + get_all_text(child)
    return text

def recurse_for_tag(elem,tag):
    comments = []
    for child in elem:
        if child.tag == tag:
            comments.append(child)
        else:
            comments.extend(recurse_for_tag(child,tag))
    return comments

def print_all(elem):
    for child in elem:
        if child.text == None:
            pass
        else:
            print child.text,
        print_all(child)
        
def get_function_info(currContainerName, function):
    currFuncName = "ERROR:INVALID_FUNCTION_NAME"
    allFuncNames = ''
    for functionName in function.findall('name'):
        if not functionName.text == None:
            currFuncName = functionName.text
            allFuncNames = allFuncNames + ' ' + currFuncName
        else:
            currFuncName = functionName.find('name').text
            allFuncNames = allFuncNames + ' ' + currFuncName
    
    #print currContainerName,'.',currFuncName
        #print currContainerName,'.',currFuncName
    allParameterListText = ''
    for parameterList in function.findall('parameter_list'):
        if not parameterList.text == None:
            parameterListText = get_all_text(parameterList)
            #print currContainerName, '.', currFuncName, '.', parameterListText
            allParameterListText = allParameterListText +  ' ' + parameterListText
        else:
            errorParamListStr = 'ERROR:BROKEN_PARAM_LIST' 
            #print errorParamListStr
            parameterListText = parameterListText + ' ' + errorParamListStr
   
    allFunctionBlockText = '' 
    for block in function.findall('block'):
        #print get_all_text(block)
        allFunctionBlockText = allFunctionBlockText + ' ' + get_all_text(block)
    
    return allFuncNames, allParameterListText, allFunctionBlockText

def convert_to_alpha_only(inString):
    pattern = re.compile('[^a-zA-Z]+')
    return pattern.sub(' ', inString)
    

'''
    takes a raw list of sets of words in a zone and converts it to the set of documents form expected by
    gensim
'''
@timed
def createbow(args, unit_items):
    
    stopWordsFilename = "/home/joshua/Applications/mallet-2.0.7/stoplists/en.txt"
    stopWordsFile = open(stopWordsFilename, 'r')
    stoplist = set([line.strip() for line in stopWordsFile])
    stopWordsFile.close()
    
    javaPlWordsFilename = 'res/javakeywords'
    cPlWordsFilename = 'res/ckeywords'
    
    selectedPlWordsFilename = ''
    if args['lang'] == 'java':
        selectedPlWordsFilename = javaPlWordsFilename
    elif args['lang'] == 'c':
        selectedPlWordsFilename = cPlWordsFilename
    else:
        raise Exception('invalid language selected: ' + args['lang'])
    
    plWordsFile = open(selectedPlWordsFilename,'r')
    plWordList = set([line.strip() for line in plWordsFile])
    plWordsFile.close()

    print ''
    print 'stop words:'
    print stoplist
    
    print ''
    print 'Listing modified unit_items...'
    docs = []
    filenames = []
    
    stemmer = Stemmer.Stemmer('english')
    
    for i, (filename, list) in enumerate(unit_items.iteritems()):
        print i, filename
        itemsStr = ' '.join(list)
        logging.warning('\t' + 'Raw:')
        logging.debug('\t' + itemsStr)
        
        itemsStr = convert_to_alpha_only(itemsStr)
        logging.warning('\t' + 'Alphabetic only:')
        logging.debug( '\t' + itemsStr)
        
        itemsStr = camelcase_sep.separateCamelCase(itemsStr)
        logging.warning( '\t' + 'Camel case separated and all lower case:')
        logging.debug( '\t' + itemsStr)
        
        doc = [word for word in itemsStr.lower().split() if word not in stoplist]
        
        logging.warning( '\t' + 'Removed stop words:')
        logging.debug( '\t' + str(doc))
        
        doc = [word for word in doc if word not in plWordList]
        
        logging.warning( '\t' + 'Removed pl words:')
        logging.debug( '\t' + str(doc))
        
        #doc = [stemming.porter2.stem(word) for word in doc]
        doc = stemmer.stemWords(doc)
        
        logging.warning( '\t' + 'Stemmed words:')
        logging.debug( '\t' + str(doc))
        
        filenames.append(filename)
        docs.append(doc)
    
    # remove words that appear only once
    '''all_tokens = sum(docs, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    docs = [[word for word in text if word not in tokens_once]
             for text in docs]
    
    
    for index,doc in enumerate(docs):
        logging.warning( filenames[index])
        logging.warning( '\t' + 'Removed words that appear only once')
        logging.debug( '\t' + str(doc))'''
    
    return docs,filenames

def cos_sim(a,b):
    denom = (np.linalg.norm(a)*np.linalg.norm(b))
    if denom == 0:
        denom = 0.0000001
    return np.dot(a,b)/denom

def conv_sparse_doc_to_full_doc(numTokens, doc):
    docFull = [0 for i in range(numTokens)]
    for id, value in doc:
        docFull[id] = value
    
    return docFull

@timed
def extract_java_toks(tree, zones):
    units = {}
    for zone in zones:
        units[zone] = {}
    
    print 'Listing classes...'
    for unit in tree.iter('unit'):
        if not unit.get('filename') == None:
            #print unit.get('filename')
            filename = unit.get('filename')
            units['class'][filename] = []
            for clas in unit.iter('class'):
                for className in clas.findall('name'):
                    if not className.text == None: #print className.text
                        units['class'][filename].append(className.text)
                    else:
                        units['class'][filename].append(className.find('name').text) #print className.find('name').text
    
    for unitFilename, classNames in units['class'].iteritems():
        print unitFilename
        for className in classNames:
            print className
    
    print ''
    print 'Listing classes with more info...'
    for unit in tree.iter('unit'):
        if not unit.get('filename') == None:
            filename = unit.get('filename')
            units['fields'][filename] = []
            units['func_names'][filename] = []
            units['params'][filename] = []
            units['func_blocks'][filename] = []
            for clas in unit.iter('class'):
                currclassName = 'ERROR:INVALID_CLASS_NAME'
                for className in clas.findall('name'):
                    if not className.text == None:
                        currClassName = className.text
                        print currClassName
                    else:
                        currClassName = className.find('name').text
                        print currClassName
                
                for decl_stmt in clas.findall('block/decl_stmt'):
                    #print get_all_text(decl_stmt)
                    units['fields'][filename].append(get_all_text(decl_stmt))
                
                for constructor in clas.iter('constructor'):
                    allFuncNames, paramText, functionText = get_function_info(currClassName, constructor)
                    units['func_names'][filename].append(allFuncNames)
                    units['params'][filename].append(paramText)
                    units['func_blocks'][filename].append(functionText)
                
                for function in clas.iter('function'):
                    allFuncNames, paramText, functionText = get_function_info(currClassName, function)
                    units['func_names'][filename].append(allFuncNames)
                    units['params'][filename].append(paramText)
                    units['func_blocks'][filename].append(functionText)
    
    for unitFilename, fieldText in units['fields'].iteritems():
        print unitFilename
        print '\t' + str(fieldText)
    
    for unitFilename, funcNames in units['func_names'].iteritems():
        print unitFilename
        print '\t' + str(funcNames)
    
    for unitFilename, params in units['params'].iteritems():
        print unitFilename
        print '\t' + str(params)
    
    for unitFilename, blocks in units['func_blocks'].iteritems():
        logging.debug( unitFilename)
        logging.debug( '\t' + str(blocks) )
    
    print ''
    print 'Listing comments of each unit...'
    for unit in tree.iter('unit'):
        if not unit.get('filename') == None:
            #print unit.get('filename')
            filename = unit.get('filename')
            units['comments'][filename] = []
            for clas in unit.iter('class'):
                '''for className in clas.findall('name'):
                if not className.text == None:
                    #print className.text
                    pass
                else:
                    #print className.find('name').text
                    pass'''
                for comment in recurse_for_tag(clas, 'comment'):
                    #print comment.text
                    units['comments'][filename].append(comment.text)
            
            commentStart = False
            for comment in unit.findall('comment'):
                if commentStart == True: #print comment.text
                    units['comments'][filename].append(comment.text)
                else:
                    commentStart = True
    
    for unitFilename, comments in units['comments'].iteritems():
        print unitFilename
        print '\t' + str(comments)
    
    return units

@timed
def extract_c_toks(tree, zones):
    units = {}
    for zone in zones:
        units[zone] = {}
    
    logging.debug('Listing variables in module scope...')
    for unit in tree.iter('unit'):
        if not unit.get('filename') == None:
            filename = unit.get('filename')
            logging.debug( 'unit filename:', filename)
            units['modvars'][filename] = []
            for modvar in unit.findall('decl_stmt'):
                modvarText = get_all_text(modvar)
                logging.debug( modvarText)
                units['modvars'][filename].append(modvarText)
    
    logging.debug( '')
    logging.debug( 'Listing functions with more info...')
    for unit in tree.iter('unit'):
        if unit.get('filename') != None:
            filename = unit.get('filename')
            units['func_names'][filename] = []
            units['params'][filename] = []
            units['func_blocks'][filename] = []
                                   
            for function in unit.iter('function'):
                allFuncNames, paramText, functionText = get_function_info(filename, function)
                logging.debug('') 
                logging.debug( allFuncNames )
                logging.debug( paramText)
                logging.debug( functionText)
                logging.debug('')
                units['func_names'][filename].append(allFuncNames)
                units['params'][filename].append(paramText)
            
            allFunctionBlockText = ''
            for block in unit.iter('block'): 
                allFunctionBlockText = allFunctionBlockText + ' ' + get_all_text(block)
                units['func_blocks'][filename].append(allFunctionBlockText)
    
    for unitFilename, funcNames in units['func_names'].iteritems():
        logging.debug( unitFilename)
        logging.debug( '\t' + str(funcNames))
    
    for unitFilename, params in units['params'].iteritems():
        logging.debug( unitFilename)
        logging.debug( '\t' + str(params))
    
    for unitFilename, blocks in units['func_blocks'].iteritems():
        logging.debug( unitFilename )
        logging.debug( '\t' + str(blocks))
    
    logging.debug( '')
    logging.debug( 'Listing comments of each unit...')
    for unit in tree.iter('unit'):
        if not unit.get('filename') == None:
            #print unit.get('filename')
            filename = unit.get('filename')
            units['comments'][filename] = []
            for clas in unit.iter('class'):
                '''for className in clas.findall('name'):
                if not className.text == None:
                    #print className.text
                    pass
                else:
                    #print className.find('name').text
                    pass'''
                for comment in recurse_for_tag(clas, 'comment'):
                    #print comment.text
                    units['comments'][filename].append(comment.text)
            
            commentStart = False
            for comment in unit.findall('comment'):
                if commentStart == True: #print comment.text
                    units['comments'][filename].append(comment.text)
                else:
                    commentStart = True
    
    for unitFilename, comments in units['comments'].iteritems():
        logging.debug( unitFilename)
        logging.debug( '\t' + str(comments))
    
    return units

@timed
def calc_sim_mine(zone, tfidfDocsFull, doc1Index, doc2Index):
    doc1Full = tfidfDocsFull[zone][doc1Index]
    doc2Full = tfidfDocsFull[zone][doc2Index] #print 'doc1Full', doc1Full
#print 'doc1np', doc1Full
# compute cosine similarity using my implementation
    cossimval = cos_sim(doc1Full, doc2Full)
    return cossimval


def calc_sim_scipy(zone, tfidfDocsNp, doc1Index, doc2Index):
    doc1np = tfidfDocsNp[zone][doc1Index]
    doc2np = tfidfDocsNp[zone][doc2Index] #print 'doc2Full', doc2Full
#print 'doc2np', doc2Full
# compute cosine similarity using scipy
    cossimval = 1-scipy.spatial.distance.cosine(doc1np, doc2np)
    return cossimval

@timed
def fast_compute_sim(zones, tfidfs, numDocs, numTokens, weights, filenames):
    assert len(weights) == len(zones)
    
    # initialize sim matrix for each zone
    sim = {}
    for zone in zones:
        sim[zone] = [ [0 for i in range(numDocs)] for j in range(numDocs)  ]
        print sim[zone]
   
    # check lengths of one sim matrix             
    assert len(sim[zones[0]]) == numDocs
    assert len(sim[zones[0]][0]) == numDocs
    
    # initialize combined sim matrix
    simCombined = [[0 for i in range(numDocs)] for j in range(numDocs)]
    
    # store each documents tfidf values
    tfidfDocs = {}
    for zone in zones:
        tfidfDocs[zone] = []
        for doc in tfidfs[zone]:
            tfidfDocs[zone].append(doc)
            
    tfidfDocsFull = {}
    for zone in zones:
        tfidfDocsFull[zone] = [ conv_sparse_doc_to_full_doc(numTokens,tfidfDocs[zone][i]) for i in xrange(numDocs) ]            
        
        
    tfidfDocsNp = {}
    for zone in zones:
        tfidfDocsNp[zone] = np.array(tfidfDocsFull[zone])#[ np.asarray(tfidfDocsFull[zone][i]) for i in xrange(numDocs) ]
    
    # compute sim matrix for each zone
    for zone in zones:
        for doc1Index in xrange(0, numDocs, 1):
            for doc2Index in xrange(doc1Index, numDocs, 1):
                if doc1Index % 10 == 0:
                    print 'current sim indices being calculated: {0},{1},{2}'.format(zone,doc1Index,doc2Index)
                
                #doc1 = tfidfDocs[zone][doc1Index]
                #doc2 = tfidfDocs[zone][doc2Index]
                
                #cossimval = calc_sim_mine(zone, tfidfDocsFull, doc1Index, doc2Index)
                cossimval = calc_sim_scipy(zone, tfidfDocsNp, doc1Index, doc2Index)
                
                sim[zone][doc1Index][doc2Index] =  0 if math.isnan(cossimval) else cossimval
                  
                sim[zone][doc2Index][doc1Index] = sim[zone][doc1Index][doc2Index]
    
    # print sim matrix for each zone            
    for zone in zones:
        print 'sim[' + zone + ']'
        for row in sim[zone]:
            print row
    
    # print sim matrix for each zone with zone name and filename
    for zone in zones:
        for i in range(numDocs):
            for j in range(numDocs):
                if not sim[zone][i][j] == 0:
                    print zone, filenames[i], filenames[j], sim[zone][i][j]
    
    # check symmetry for sim matrices              
    for zone in zones:
        for i in xrange(0,numDocs,1):
            for j in xrange(i,numDocs,1):
                #print '({0},{1})'.format(i,j),
                assert sim[zone][i][j] == sim[zone][j][i]
            #print ''36
    
    # create combined sim matrix
    for zoneIndex, zone in enumerate(zones):
        for i in range(0, numDocs, 1):
            for j in range(0, numDocs, 1):
                if i == j:
                    print 'weights[zoneIndex]', weights[zoneIndex]
                    print 'sim[zone][i][j]', sim[zone][i][j]
                    
                simCombined[i][j] += weights[zoneIndex]*sim[zone][i][j]
                
    return simCombined
               
def gaac_sim(cluster1, cluster2, sim):
    sumCosSim = 0
    for i in cluster1:
        for j in cluster2:
            sumCosSim += sim[i][j]
            
    if sumCosSim == 0:
        return 0
            
    denom = (len(cluster1)+len(cluster2))*(len(cluster1)+len(cluster2)-1)
    
    return sumCosSim/denom

@timed
def createobs(sysname, zones, docs, filenames, numDocs, giantDict, numTokens):
    obs = []
    # initialize obs
    for numDoc in range(numDocs):
        obs.append([0 for numToken in range(len(zones) * numTokens)])
    
    mycorpora = {}
    tfidfs = {}
    id2token = {}
    for zoneIndex, zone in enumerate(zones):
        id2token[zone] = {}
        for token, id in giantDict.token2id.iteritems():
            id2token[zone][id] = token
        
        mycorpora[zone] = [giantDict.doc2bow(doc) for doc in docs[zone]]
        corpora.MmCorpus.serialize('/tmp/' + sysname + '_' + zone + '.mm', mycorpora[zone]) # store to disk, for later use
        print mycorpora[zone]
        tfidfModel = models.TfidfModel(mycorpora[zone]) # step 1 -- initialize a model
        tfidfs[zone] = tfidfModel[mycorpora[zone]]
        print ''
        print 'Analyzing zone ' + zone
        for index, doc in enumerate(tfidfs[zone]):
            print filenames[index], doc
        
        print ''
        print 'Total number of tokens for zone ' + zone + ': ' + str(len(id2token[zone].keys()))
        #obs.append( [0 for key in range(len(id2token[zone].keys())) ] )
        print ''
        print 'Printing tokens with ids and tfidfModel values for zone ' + zone + ':'
        for index, doc in enumerate(tfidfs[zone]):
            for id, value in doc:
                print filenames[index] + ' ' + id2token[zone][id] + ' ' + str(id) + "," + str(value)
    
    #obs[index].append(value)
    for zoneIndex, zone in enumerate(zones):
        for tfidfIndex, doc in enumerate(tfidfs[zone]):
            for id, value in doc:
                colIndex = zoneIndex * numTokens + id
                obs[tfidfIndex][colIndex] = value
    
    for row in obs:
        print len(row), ' - ', row
    
    numZeros = []
    for row in obs:
        numZeros.append([val for val in row if val == 0])
    
    print ''
    print 'Number of zeros in rows:'
    for row in numZeros:
        print len(row)
    
    #for zoneIndex,obsRow in enumerate(obs):
    #    for termIndex,obsCol in enumerate(obsRow):
    #       print zones[zoneIndex] + ':' + id2token[zones[zoneIndex]][termIndex] + ':' + str(termIndex) + ':' + str(obs[zoneIndex][termIndex]),
    return obs, tfidfs, id2token

@timed
def calcweights(zones, filenames, initialWeights, obs, tfidfs, id2token):
    g = mixture.GMM(n_components=len(zones),n_iter=500)
    print 'original initial weights', g.weights_
    #g.fit(obs)
    #print 'weights', g.weights_
    #print 'means', g.means_
    #print 'covars', g.covars_
    #g = mixture.GMM(n_components=len(zones))
    g.weights_ = initialWeights
    print 'zone-tokens-based initial weights', g.weights_
    g.fit(obs)
    print 'weights', g.weights_
    print 'means', g.means_
    print 'covars', g.covars_
    print ''
    for zoneIndex, zone in enumerate(zones):
        for docIndex, doc in enumerate(tfidfs[zone]):
            print zone, filenames[docIndex]
            print [id2token[zone][id] + ' ' + str(id) + "," + str(value) for id, value in doc]
    
    return g.weights_

def max_indices(mat):
    maxIdxForEachRow = mat.argmax(0)
    maxValsForEachCol = np.array([mat[rowPos][colPos] for colPos,rowPos in enumerate(maxIdxForEachRow)])
    maxPosCol = maxValsForEachCol.argmax()
    maxPosRow = maxIdxForEachRow[maxPosCol]
    maxVal = mat[maxPosRow][maxPosCol]
    return maxVal,maxPosRow,maxPosCol

@timed
def most_sim_clusterpair(sim, clusters):
    maxSimVal = -1
    for i in xrange(0, len(clusters), 1):
        for j in range(i, len(clusters), 1):
            if i != j:
                if sim[i][j] > maxSimVal:
                    maxSimVal = sim[i][j]
                    maxi = i
                    maxj = j
    
    return maxSimVal, maxi, maxj


def del_old_vals(sim, clusters, maxi, maxj):
    greaterIndex = maxi
    lesserIndex = maxj
    if maxj > maxi:
        greaterIndex = maxj
        lesserIndex = maxi
    #del sim[greaterIndex]
    sim = np.delete(sim,greaterIndex,axis=0)
    #for row in sim:
        #del row[greaterIndex]
    sim = np.delete(sim,greaterIndex,axis=1)
    
    #del sim[lesserIndex]
    sim = np.delete(sim,lesserIndex,axis=0)
    #for row in sim:
    #    del row[lesserIndex]
    sim = np.delete(sim,lesserIndex,axis=1)
    
    del clusters[greaterIndex]
    del clusters[lesserIndex]
    
    return sim

def check_sim_dims(sim, clusters):
    assert len(sim) == len(clusters)
    for rowIndex, row in enumerate(sim):
        assert len(row) == len(clusters)


def add_new_simrows(sim, clusters, newRow):
    for rowIndex, row in enumerate(sim):
        if rowIndex != len(clusters) - 1:
            row.append(newRow[rowIndex])

def runclustering(filenames, numDocs, sim):
    print 'python sim:'
    print sim[0]
    sim = np.array(sim)
    origSim = np.array(sim)
    for i in xrange(numDocs):
        sim[i][i] = 0
    print 'numpy sim:'
    print sim[0]
    
    clusters = []
    for i in range(numDocs):
        cluster = set()
        cluster.add(i)
        clusters.append(cluster)
    
    cutoff = int(len(clusters) * 0.1)
    while len(clusters) != cutoff:
        maxi = -1
        maxj = -1
        #maxSimVal, maxi, maxj = most_sim_clusterpair(sim, clusters)
        maxSimVal, maxi, maxj = max_indices(sim)
        
        notallzeros = 'maxi == maxj and sim matrix is not all zeros'
        if maxi == maxj:
            for i in xrange(len(sim)):
                for j in xrange(i,len(sim),1):
                    assert sim[i][j] == 0, notallzeros
                    assert sim[j][i] == 0, notallzeros
        
        assert maxSimVal != -1
        assert maxi != -1
        assert maxj != -1
        print 'max sim val: {0}'.format(maxSimVal)
        print 'max i ({0}): {1}'.format(maxi, [filenames[i] for i in clusters[maxi]])
        print 'max j ({0}): {1}'.format(maxj, [filenames[i] for i in clusters[maxj]])
        newCluster = clusters[maxi] | clusters[maxj]
        sim = del_old_vals(sim, clusters, maxi, maxj)
        clusters.append(newCluster)
        newRow = [gaac_sim(newCluster, cluster, origSim) for cluster in clusters]
        expsim = np.zeros((len(sim)+1,len(sim)+1))
        expsim[:len(sim),:len(sim)] = sim
        sim = expsim
        for pos, val in enumerate(newRow):
            sim[-1][pos] = val
            sim[pos][-1] = val
        sim[-1][-1] = 0
        #add_new_simrows(sim, clusters, newRow)
        
        print ''
        print newRow
        #sim.append(newRow)
        print sim
        check_sim_dims(sim, clusters)
    
    return clusters

@timed
def writeclustersfile(args, sysname, filenames, clusters):
    datadir = 'data'
    if not os.path.exists(datadir):
        os.makedirs(datadir)
    if args['weights'] == 'uni':
        outputClustersRsfFilename = datadir + '/' + sysname + '_zclusters_uniweights.rsf'
    elif args['weights'] == 'em':
        outputClustersRsfFilename = datadir + '/' + sysname + '_zclusters_emweights.rsf'
    else:
        raise Exception('invalid weights selected')
    out = open(outputClustersRsfFilename, 'w')
    for clusterIndex, cluster in enumerate(clusters):
        for filenameIndex in cluster:
            entityName = None
            if args['lang'] == 'java':
                entityName = string.replace(string.replace(filenames[filenameIndex], '/', '.'), '.java', '')
            elif args['lang'] == 'c':
                entityName = filenames[filenameIndex]
            else:
                raise Exception('Invalid language')
            rsfLine = 'contain {0} {1}'.format(clusterIndex, entityName)
            print rsfLine
            out.write(rsfLine + '\n')
    
    out.close()


def interact():
    import code
    code.InteractiveConsole(locals=globals()).interact()

@timed
def exec_first_phase(args,sysname,tree):
    zones = None
    units = None
    if args['lang'] == 'java':
        zones = ['class', 'fields', 'func_names', 'params', 'func_blocks', 'comments']
        units = extract_java_toks(tree, zones)
    elif args['lang'] == 'c':
        zones = ['modvars', 'func_names', 'params', 'func_blocks', 'comments']
        units = extract_c_toks(tree, zones)
    
    '''
    hp = hpy()
    hp.setrelheap()
    h = hp.heap()
    '''
        
    docs = {}
    filenames = []
    docsAllZones = []
    for zone in zones:
        print 
        print 'creating bow for ' + zone
        docs[zone], filenames = createbow(args, units[zone])
        for doc in docs[zone]:
            docsAllZones.append(doc)
            
    #import pdb; pdb.set_trace()
    
    numTokensInZone = {}
    for zone in zones:
        numTokensInZone[zone] = 0
    
    for zone in zones:
        for doc in docs[zone]:
            logging.debug(zone, doc)
            for word in doc:
                numTokensInZone[zone] += 1
    
    totalTokensAcrossAllZones = 0
    for zone in zones:
        totalTokensAcrossAllZones += numTokensInZone[zone]
    
    print ''
    for zone in zones:
        print 'number of tokens in zone', zone, numTokensInZone[zone]
    
    print 'number of tokens across all zones', totalTokensAcrossAllZones
    tokenBasedWeights = []
    for zone in zones:
        denom = float(totalTokensAcrossAllZones)
        if denom == 0:
            denom = .00001
        numer = float(numTokensInZone[zone])
        tokenBasedWeights.append(numer / denom)
        
    equalWeights = []
    for zone in zones:
        equalWeights.append(float(1) / float(len(zones)))
    
    print 'initial weights based on tokens in zone:'
    print tokenBasedWeights
    
    selectedWeights = []
    if args['weights'] == 'uni':
        selectedWeights = equalWeights
    elif args['weights'] == 'em':
        selectedWeights = tokenBasedWeights
    else:
        raise Exception('invalid weight selection: {0}'.format(args['weights']))
    
# create one row in obs for each document
    numDocs = len([doc for doc in docs[zones[0]]])
    assert len(units[zones[0]].keys()) == numDocs
    giantDict = corpora.Dictionary(docsAllZones)
    giantDict.save('/tmp/' + sysname + '.dict') # store the dictionary, for future reference
    print giantDict
    numTokens = len(giantDict.token2id.keys())
    print 'total number of tokens from giantDict: ', numTokens
    obs, tfidfs, id2token = createobs(sysname, zones, docs, filenames, numDocs, giantDict, numTokens)
    print 'size of obs: ', sys.getsizeof(obs)
    emweights = calcweights(zones, filenames, selectedWeights, obs, tfidfs, id2token)
#compute_sim(zones, tfidfs, numTokens, sim)
    
    
    
    simFilename = '/tmp/' + sysname + '_sim.pkl'
    sim = None
    simFile = None
    usingSavedSim = False
    sim = fast_compute_sim(zones, tfidfs, numDocs, numTokens, emweights, filenames)
    simFile = open(simFilename, 'w')
    pickle.dump(sim, simFile)
#     if os.path.isfile(simFilename) and usingSavedSim:
#         simFile = open(simFilename,'r')
#         sim = pickle.load(simFile)
#     else:
#         sim = fast_compute_sim(zones, tfidfs, numDocs, numTokens, selectedWeights, filenames)
#         simFile = open(simFilename,'w')
#         pickle.dump(sim,simFile)
#     simFile.close()
    print ''
    print 'Doc sim matrix:'
    for row in sim:
        print row
    
    return filenames, numDocs, sim

def main():
    '''query = 'comment'
    for elem in tree.iter(tag='comment'):
        print elem.tag, elem.text  
    exit()'''
    
    args, sysname, tree = setup()
    
    filenames, numDocs, sim = exec_first_phase(args,sysname,tree)
        
    clusters = runclustering(filenames, numDocs, sim)
    
    writeclustersfile(args, sysname, filenames, clusters)

if __name__ == '__main__':
    cProfile.run('main()','main.prof')

            

                
            