'''
Created on Mar 23, 2013

@author: joshua
'''

import sys, argparse

def main(inArgs):
    parser = argparse.ArgumentParser()
    parser.add_argument('--pkgprefixes', type=str, nargs='+', required=True)
    parser.add_argument('--infile', type=str, required=True)
    parser.add_argument('--outfile', type=str, required=True)
    parser.add_argument('--delimiter',type=str,default=".")
    args = vars(parser.parse_args(inArgs))
    
    pkgprefixes = args['pkgprefixes']
    infilename = args['infile']
    outfilename = args['outfile']
    delimiter = args['delimiter']
    infile = open(infilename,'r')
    
    #for line in infile:
    #    print line,
    
    dirtyfacts = []
    for line in infile:
        fact = line.split()
        dirtyfacts.append(fact)
        
    infile.close()
    
    classes = set()
    for fact in dirtyfacts:
        classes.add(fact[1])
        classes.add(fact[2])
        
    filteredClasses = [clas for pkgprefix in pkgprefixes for clas in classes if clas.startswith(pkgprefix)]
    
    clusters = []
    for clas in filteredClasses:
        parts = clas.split(delimiter)
        pkg = delimiter.join(parts[0:-1])
        
        if pkg == "":
            pkg = "default.ss"
        
        className = parts[-1]
        clusters.append([pkg,clas])
        
    clusters.sort()
    out = open(outfilename,'w')
    for cluster in clusters:
        print cluster
        line = 'contain {0} {1}\n'.format(cluster[0],cluster[1])
        out.write(line)

# creates authoritative clustering in rsf format using packages
if __name__ == '__main__':
    main(sys.argv[1:])
        