'''
Created on Mar 23, 2013

@author: joshua
'''

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sourcefile', type=str, required=True)
    parser.add_argument('--authfile', type=str, required=True)
    parser.add_argument('--outfile', type=str,required=True)
    args = vars(parser.parse_args())
    
    sourcefile = open(args['sourcefile'],'r')
    sourcefacts = []
    for line in sourcefile:
        fact = line.split()
        sourcefacts.append(fact)
    sourcefile.close()

    sourceclasses = set()
    for fact in sourcefacts:
        sourceclasses.add(fact[2])
        
    authfile = open(args['authfile'],'r')
    authfacts = []
    for line in authfile:
        fact = line.split()
        authfacts.append(fact)
        
    authclasses = set()
    for fact in authfacts:
        authclasses.add(fact[2])
        
    authonlyclasses = authclasses - sourceclasses
    for clas in authonlyclasses:
        print clas
        
    
    #sourceonlyclasses =  sourceclasses - authclasses
    #for clas in sourceonlyclasses:
    #    print clas
        
    cleansourcefacts = []
    for fact in authfacts:
        if fact[2] in sourceclasses:
            cleansourcefacts.append(fact)
            
    out = open(args['outfile'],'w')
    for fact in cleansourcefacts:
        out.write('{0} {1} {2}\n'.format(fact[0],fact[1],fact[2]))
    out.close()