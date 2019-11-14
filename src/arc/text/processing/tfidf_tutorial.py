'''
Created on Mar 17, 2013

@author: joshua
'''


import logging
import stemming.porter2
import re
from gensim import corpora, models, similarities

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def separateCamelCase(name):
    s1 = first_cap_re.sub(r'\1 \2', name)
    return all_cap_re.sub(r'\1 \2', s1).lower()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    
    documents = ["Human machine interface for lab abc computer applications",
              "A survey of user opinion of computer system response time",
              "The EPS user interface management system",
              "System and human system engineering testing of EPS",
              "Relation of user perceived response time to error measurement",
              "The generation of random binary unordered trees",
              "The intersection graph of paths in trees",
              "Graph minors IV Widths of trees and well quasi ordering",
              "Graph minors A survey"]

    
    # remove common words and tokenize
    stoplist = set('for a of the and to in'.split())
    texts = [[word for word in document.lower().split() if word not in stoplist]
         for document in documents]

    # remove words that appear only once
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
             for text in texts]
    
    # stem words
    texts = [[stemming.porter2.stem(word) for word in text]
             for text in texts]

    print ''
    print 'Printing texts...'
    print texts
    
    dictionary = corpora.Dictionary(texts)
    dictionary.save('/tmp/deerwester.dict') # store the dictionary, for future reference
    print dictionary
    
    print dictionary.token2id
    
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus) # store to disk, for later use
    print corpus
    
    tfidfModel = models.TfidfModel(corpus) # step 1 -- initialize a model

    corpus_tfidf = tfidfModel[corpus]

    print ''    
    for doc in corpus_tfidf:
        print doc
        
    print ''
    for doc in corpus_tfidf:
        for (id,value) in doc:
            print str(id) + ","+ str(value)


