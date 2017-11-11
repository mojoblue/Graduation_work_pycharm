from bs4 import BeautifulSoup
from urllib.request import HTTPError
import urllib.parse
import requests

from konlpy.tag import Komoran

import networkx
import re

from itertools import repeat
from multiprocessing import Pool
import operator

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
 
        return both
 
    def summarize(self, ratio = 0.333):
        r = self.rank()
        ks = sorted(r, key=r.get, reverse=True)[:int(len(r)*ratio)]
        return ' '.join(map(lambda k:self.dictCount[k], sorted(ks)))

class WebTool(object):
    def __init__(self):
        self.init_url = "https://www.google.co.kr/search?q="
        self.nav_url = "https://search.naver.com/search.naver?query="
        self.hdr = {'User-Agent': 'Mozilla/5.0'}

    def getLinks(self, query, **kargs):
        
        links = []

        query = query.replace(" ", "+")
        query_url = self.init_url + urllib.parse.quote_plus(query)

        if "site" in kargs.keys():
            query_url = query_url + "+site%3A" + kargs["site"]

        if "max_pages" in kargs.keys():
            query_url = query_url + "&num=" + kargs["max_pages"]
  
        result = requests.get(query_url, headers=self.hdr, timeout=10)
        html = result.content
        soup = BeautifulSoup(html, 'lxml')
            
        for item in soup.find_all('h3', attrs={'class' : 'r'}):
            links.append(urllib.parse.unquote_plus(item.a['href'][7:].split('&')[0]))

        return  links

    def getRelated(self, query):
        cards = []
        nav_url = self.nav_url + urllib.parse.quote_plus(query.replace(" ", "+"))
    
        result = requests.get(nav_url, headers=self.hdr, timeout=10)
        html = result.content
        soup = BeautifulSoup(html, 'lxml')

        relate_list = soup.find('dd', attrs={'class' : 'lst_relate'}).find_all('a')
        
        for item in relate_list:
            cards.append(urllib.parse.unquote_plus(item.text).strip())
        
        return cards
        

    def parseText(self, url):
    
        bodyTxt = ""
        try:
            result = requests.get(url, headers=self.hdr, timeout=10)
            html = result.content
            soup = BeautifulSoup(html, 'lxml')
            paragraphs = soup.find_all('p')
            
            for p in paragraphs:
                txt = p.getText().strip()
                if txt is not '':
                    for line in txt.split("\n"):
                        bodyTxt += line
                    
        except HTTPError as e:
            bodyTxt = ""
            return bodyTxt

        finally:
            return bodyTxt.replace("\xa0", " ")

def callSummary(text):
    tagger = Komoran()
    stopword = set([('있', 'VV'), ('하', 'VV'), ('되', 'VV') ])
    txtRank = TextRank()
    txtRank.loadSents(RawSentence(text), lambda sent: filter(lambda x:x not in stopword and x[1] in ('NNG', 'NNP', 'VV', 'VA'), tagger.pos(sent)))
    txtRank.build()
            
    return txtRank.summarize(0.3)#.replace("\xa0", " ")

def callKeyword(text):

    keywords = []
    
    stopword = set([('있', 'VV'), ('하', 'VV'), ('되', 'VV') ])
    txtRank = TextRank()
    for line in text.split("\n"):
        txtRank.load(RawTagger(line), lambda w: w not in stopword and (w[1] in ('NNG', 'NNP')))
    txtRank.build()
    
    kw = txtRank.extract(0.1)
    for k in sorted(kw, key=kw.get, reverse=True):
        if len(k) == 2: keywords.append((k[0][0]+" "+k[1][0], kw[k]))
        else: keywords.append((k[0][0], kw[k]))

    return keywords
     
class KwordModule(object):

    def __init__(self):
        self.wtool = WebTool()

    def getDocData(self, url):

        text = self.wtool.parseText(url)
        summary = callSummary(text)
        keyword = callKeyword(text)
        
        return (summary, keyword)

    def toSummary(self, query, pnum, knum):
        
        url_list = self.wtool.getLinks(query, site="tistory.com", max_pages='{}'.format(pnum))

        # cards = self.wtool.getRelated(query)
        
        wiki_url = "https://ko.wikipedia.org/wiki/"+urllib.parse.quote_plus(query)

        # wiki_res = self.getDocData(wiki_url)
        
        multiprocess = Pool(4)  # Pool tells how many at a time
        res = multiprocess.map(self.getDocData, url_list)
        multiprocess.terminate()
        multiprocess.join()

        keywords = dict()
        for r in res:
            for k, v in r[1]:
                if k not in keywords:
                    keywords[k] = v
                elif  v > keywords[k]:
                    keywords[k] = v
 
        sorted_kword = sorted(keywords.items(), key=operator.itemgetter(1), reverse=True)
        keywords = []
        for i in sorted_kword[:knum+1]:
            keywords.append(i[0])

        kwordSet = set(keywords)
        str = list(kwordSet)
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

        return ",\n".join(str_list)

# if __name__=='__main__':
#
#     kmodule = KwordModule()
#     keywords_str = kmodule.toSummary("에펠탑", 2, 20)
#     print(keywords_str)
    # print('wiki',wiki)
    # print('res',res)
    # print('keyword',keywords)
    # print('card',cards)

    # print(keywords)

