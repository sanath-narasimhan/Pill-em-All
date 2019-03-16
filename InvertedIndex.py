import numpy as np
import pandas as pd
import pickle
import string 
import html
import ast
import re
from nltk.corpus import stopwords
stpwrds = stopwords.words("english")
from nltk.stem import WordNetLemmatizer

def encode_reviews(review):
    return html.unescape(review)

def rm_stopword(r):
    r_n = " ".join([i for i in r if i not in stpwrds])
    return r_n
    
def lem(tokens):
    l = WordNetLemmatizer()
    out = [l.lemmatize(word) for word in tokens]
    return out 

def InvertedIndex():
    data = pd.read_csv('drugData_full.csv', index_col='Unnamed: 0')
    data['review'] = data['review'].apply(encode_reviews)
    reviews = data['review'].str.replace("[^a-zA-Z]", " ")
    reviews = reviews.apply(lambda r: " ".join([w for w in r.split() if len(w)>2]))
    reviews = [rm_stopword(r.split()) for r in reviews]
    reviews = [r.lower() for r in reviews]
    reviews = pd.Series(reviews)
    tokenizd = reviews.apply(lambda r: r.split())
    reviews = tokenizd.apply(lem)

    vocabulary = {}

    for i,r in enumerate(reviews, start=0):
        for j,w in enumerate(r , start=0):
            if w not in vocabulary:
                vocabulary[w] = [1,{i:[j]}]
            else:
                if i not in vocabulary[w][1]:
                    vocabulary[w][0] += 1
                    vocabulary[w][1][i] = [j]
                else:
                    vocabulary[w][1][i].append(j)
    
    N = np.float64(data.shape[0])
    
    for w in vocabulary.keys():
        pl = {}
        for i in vocabulary[w][1].keys():
            tf = (len(vocabulary[w][1][i])/len(reviews[i]))
            wi = (1 + np.log10(tf)) * np.log10(N/vocabulary[w][0])
            pl[i] = wi
        vocabulary[w].append(pl)
    
    p = open('drugVocab.pickel',"wb")
    pickle.dump(vocabulary,p)


def topk(query):
    data = pd.read_csv('drugData_full.csv', index_col='Unnamed: 0')
    p = open('drugVocab.pickel',"rb")
    vocabulary = pickle.load(p)

    q = query.replace("[^a-zA-Z]", " ").lower()
    q_vec = rm_stopword(q.split())
    q_vect = lem(q_vec.split())
    
    srtdpl = {}
    qw = {}
    for w in q_vect:
        if w in vocabulary.keys():
            if w not in srtdpl.keys():
                srtdpl[w] = sorted(vocabulary[w][2].items(), key=lambda x:x[1], reverse=True)[:10]
        if w not in qw:
            qw[w] = [1,(1/len(q_vect))]
        elif w in qw:
            qw[w][0] += 1
            qw[w][1] = (qw[w][0]/len(q_vect))
    if srtdpl == {}:
        return "No results found"
    
    topk = []
    N = data.shape[0]
    for i in range(N):
        count = 0
        sd = 0
        for w in q_vect:
            for (di,wt) in srtdpl[w]:
                if di == i: count += 1
        if count > 0 and count == len(q_vect):
            for w in q_vect:
                l = [x for x in srtdpl[w] if x[0] == i]
                sd += l[0][1] * qw[w][1]
            topk.append((i,sd))
        elif count > 0 and count < len(q_vec):
            for w in q_vect:
                l = srtdpl[w][9]
                sd += l[1] * qw[w][1]
            topk.append((i,sd))    
            
    show = [x for x in sorted(topk, key=lambda i:i[1], reverse=True)]        
    out = []
    for (ind,s) in show:
        out.append( [data.loc[data.index[ind], 'drugName'], data.loc[data.index[ind], 'usefulCount'], data.loc[data.index[ind], 'condition'], data.loc[data.index[ind], 'rating'], data.loc[data.index[ind], 'review'], s*100])
    pd.set_option('display.max_columns', -1)  
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('max_colwidth', -1)
 
    out =  pd.DataFrame(out, columns=['Drug Name','Useful count','Condition','Rating(/10)','Review','Similarity%'])
 
    return out    