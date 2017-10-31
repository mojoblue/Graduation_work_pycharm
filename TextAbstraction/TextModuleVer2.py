
'''
This module made Hyunsoo, Kim
'''
from bs4 import BeautifulSoup
from urllib.request import HTTPError
from urllib.parse   import quote

from konlpy.tag import Komoran

import requests
import networkx
import re

class RawSentence:
    def __init__(self, textIter):
        if type(textIter) == str: self.textIter = textIter.split('\n')
        else: self.textIter = textIter
        self.rgxSplitter = re.compile('([.!?:](?:["\']|(?![0-9])))')
 
    def __iter__(self):
        for line in self.textIter:
            ch = self.rgxSplitter.split(line)
            for s in map(lambda a, b: a + b, ch[::2], ch[1::2]):
                if not s: continue
                yield s
 
class RawTagger:
    def __init__(self, textIter, tagger = None):
        if tagger:
            self.tagger = tagger
        else :
            from konlpy.tag import Komoran
            self.tagger = Komoran()
        if type(textIter) == str: self.textIter = textIter.split('\n')
        else: self.textIter = textIter
        self.rgxSplitter = re.compile('([.!?:](?:["\']|(?![0-9])))')
 
    def __iter__(self):
        for line in self.textIter:
            ch = self.rgxSplitter.split(line)
            for s in map(lambda a,b:a+b, ch[::2], ch[1::2]):
                if not s: continue
                yield self.tagger.pos(s)
 
class TextRank:
    def __init__(self, **kargs):
        self.graph = None
        self.window = kargs.get('window', 5)
        self.coef = kargs.get('coef', 1.0)
        self.threshold = kargs.get('threshold', 0.005)
        self.dictCount = {}
        self.dictBiCount = {}
        self.dictNear = {}
        self.nTotal = 0
 
 
    def load(self, sentenceIter, wordFilter = None):
        def insertPair(a, b):
            if a > b: a, b = b, a
            elif a == b: return
            self.dictBiCount[a, b] = self.dictBiCount.get((a, b), 0) + 1
 
        def insertNearPair(a, b):
            self.dictNear[a, b] = self.dictNear.get((a, b), 0) + 1
 
        for sent in sentenceIter:
            for i, word in enumerate(sent):
                if wordFilter and not wordFilter(word): continue
                self.dictCount[word] = self.dictCount.get(word, 0) + 1
                self.nTotal += 1
                if i - 1 >= 0 and (not wordFilter or wordFilter(sent[i-1])): insertNearPair(sent[i-1], word)
                if i + 1 < len(sent) and (not wordFilter or wordFilter(sent[i+1])): insertNearPair(word, sent[i+1])
                for j in range(i+1, min(i+self.window+1, len(sent))):
                    if wordFilter and not wordFilter(sent[j]): continue
                    if sent[j] != word: insertPair(word, sent[j])
 
    def loadSents(self, sentenceIter, tokenizer = None):
        import math
        def similarity(a, b):
            n = len(a.intersection(b))
            return n / float(len(a) + len(b) - n) / (math.log(len(a)+1) * math.log(len(b)+1))
 
        if not tokenizer: rgxSplitter = re.compile('[\\s.,:;-?!()"\']+')
        sentSet = []
        for sent in filter(None, sentenceIter):
            if type(sent) == str:
                if tokenizer: s = set(filter(None, tokenizer(sent)))
                else: s = set(filter(None, rgxSplitter.split(sent)))
            else: s = set(sent)
            if len(s) < 2: continue
            self.dictCount[len(self.dictCount)] = sent
            sentSet.append(s)
 
        for i in range(len(self.dictCount)):
            for j in range(i+1, len(self.dictCount)):
                s = similarity(sentSet[i], sentSet[j])
                if s < self.threshold: continue
                self.dictBiCount[i, j] = s
 
    def getPMI(self, a, b):
        import math
        co = self.dictNear.get((a, b), 0)
        if not co: return None
        return math.log(float(co) * self.nTotal / self.dictCount[a] / self.dictCount[b])
 
    def getI(self, a):
        import math
        if a not in self.dictCount: return None
        return math.log(self.nTotal / self.dictCount[a])
 
    def build(self):
        self.graph = networkx.Graph()
        self.graph.add_nodes_from(self.dictCount.keys())
        for (a, b), n in self.dictBiCount.items():
            self.graph.add_edge(a, b, weight=n*self.coef + (1-self.coef))
 
    def rank(self):
        return networkx.pagerank(self.graph, weight='weight')
 
    def extract(self, ratio = 0.1):
        ranks = self.rank()
        cand = sorted(ranks, key=ranks.get, reverse=True)[:int(len(ranks) * ratio)]
        pairness = {}
        startOf = {}
        tuples = {}
        for k in cand:
            tuples[(k,)] = self.getI(k) * ranks[k]
            for l in cand:
                if k == l: continue
                pmi = self.getPMI(k, l)
                if pmi: pairness[k, l] = pmi
 
        for (k, l) in sorted(pairness, key=pairness.get, reverse=True):
            #print(k[0], l[0], pairness[k, l])
            if k not in startOf: startOf[k] = (k, l)
 
        for (k, l), v in pairness.items():
            pmis = v
            rs = ranks[k] * ranks[l]
            path = (k, l)
            tuples[path] = pmis / (len(path) - 1) * rs ** (1 / len(path)) * len(path)
            last = l
            while last in startOf and len(path) < 7:
                if last in path: break
                pmis += pairness[startOf[last]]
                last = startOf[last][1]
                rs *= ranks[last]
                path += (last,)
                tuples[path] = pmis / (len(path) - 1) * rs ** (1 / len(path)) * len(path)
 
        used = set()
        both = {}
        for k in sorted(tuples, key=tuples.get, reverse=True):
            if used.intersection(set(k)): continue
            both[k] = tuples[k]
            for w in k: used.add(w)
 
        #for k in cand:
        #    if k not in used or True: both[k] = ranks[k] * self.getI(k)
 
        return both
 
    def summarize(self, ratio = 0.333):
        r = self.rank()
        ks = sorted(r, key=r.get, reverse=True)[:int(len(r)*ratio)]
        return ' '.join(map(lambda k:self.dictCount[k], sorted(ks)))

class searchGoogl(object):
    def __init__(self):
        self.queryURL = "https://www.google.co.kr/search?q="
        self.query = ""
    
    def clearQuery(self):
        self.query = ""

    def setQuery(self, query):
        self.clearQuery()
        query = query.replace(" ", "+")
        self.query = quote(query)

    def getLinks(self, query, **kargs):
        links = []
        cards = []
        self.setQuery(query)

        if "site" not in kargs.keys():
            self.queryURL = self.queryURL + self.query #+ quote(query)
        else:
            site = kargs["site"]
            self.queryURL = self.queryURL + self.query + "+site%3A" + site
            
        hdr = {'User-Agent': 'Mozilla/5.0'}
        result = requests.get(self.queryURL, headers=hdr)
        html = result.content
    
        soup = BeautifulSoup(html, 'lxml')

        for item in soup.find_all('h3', attrs={'class' : 'r'}):
            links.append(item.a['href'][7:].split('&')[0])

        return  links

class extractBodyTxt(object):
    def getText(self, url):

        hdr = {'User-Agent': 'Mozilla/5.0'}
        '''
        result = requests.get(url, headers=hdr)
        html = result.content
        '''
        bodyText = ""

        try:
            result = requests.get(url, headers=hdr)
            html = result.content
       
        except HTTPError as e:

            bodyText = ""
            #return bodyText
            return bodyText

        else:
            
            soup = BeautifulSoup(html, 'lxml')

            paragraphs = soup.find_all('p')
            b = ""
            for p in paragraphs:
                txt = p.getText().strip()
                if txt is not '':
                    for line in txt.split("\n"):
                        bodyText += line
                        
            
            return bodyText

class moduleKword(object):

    def __init__(self):
        self.searchGoo = searchGoogl()
        self.extractor = extractBodyTxt()
        self.tagger = Komoran()
        self.stopword = set([('있', 'VV'), ('하', 'VV'), ('되', 'VV') ])
        self.sites = []
        #self.query = ""

    def setOn(self, query):
        self.query = query
        #self.urls = self.searchGoo.getLinks(self.query)
        
    def addStopword(self, stopword_list):
        self.stopword.update(stopword_list)
        '''
        for sword in stopword_list:
            self.stopword.add(s)
        '''

    def getSummar(self, query):
        summResults = []
        kwordResults = []
        urls = self.searchGoo.getLinks(query, site="tistory.com")

        for url in urls:
            paragraphs = self.extractor.getText(url)
            
            if len(paragraphs) is not 0:
                kwords =[]
                # txtRank = TextRank()
                kwordRank = TextRank()
                # txtRank.loadSents(RawSentence(paragraphs), lambda sent: filter(lambda x:x not in self.stopword and x[1] in ('NNG', 'NNP', 'VV', 'VA'), self.tagger.pos(sent)))
                
                for line in paragraphs.split("\n"):
                    kwordRank.load(RawTagger(line), lambda w: w not in self.stopword and (w[1] in ('NNG', 'NNP')))#, 'VV', 'VA')))

                #txtRank.load(d)
                # txtRank.build()
                kwordRank.build()
      
                # summResults += [txtRank.summarize(0.3)]
                kw = kwordRank.extract(0.1)
                for k in sorted(kw, key=kw.get, reverse=True):
                    if len(k) == 2: kwords.append(k[0][0]+" "+k[1][0])
                    else:
                        kwords += [k[0][0]]
                kwordResults.append(kwords)
        '''
        for k in sorted(ranks, key=ranks.get, reverse=True)[:100]:
            print("\t".join([str(k), str(ranks[k]), str(tr.dictCount[k])]))
        '''
        return kwordResults

# 사용법
# mk = moduleKword()

# 한 사이트 당 요약문, 키워드 추출
def makeResult(query):
    mk = moduleKword()
    # summs, kwords = mk.getSummar("에펠탑")
    kwords = mk.getSummar(query)
    kwordSet = set([])
    for k in kwords:
        for keyword in k:
            kwordSet.add(keyword)
    str = list(kwordSet)[:15]
    added_str = ""
    str_list = []
    for s in str:
        if len(added_str + s) <= 30:
            if len(added_str) == 0:
                added_str += s
            else:
                added_str += ", " + s
        else:
            str_list.append(added_str)
            added_str = ""
            added_str += s

    return "\n, ".join(str_list)

# keyword_str = makeResult("브란덴부르크 문")
# print(keyword_str)
# print("\n".join(summs))