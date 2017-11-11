# KeywordExtractor

검색된 블로그들의 요약문, 키워드 제시, 멀티 프로세싱으로 처리

## Dependency Package:
BeautifulSoup

urllib

requests

konlpy

networkx

## How to use:

    kmodule = KwordModule()

    wiki_summ, summ_res, keywords, cards = kmodule.toSummary("에펠탑", 10, 15)

__1 Parameter:__

검색할 키워드(String)

요약할 문서 수(Integer)

추출할 키워드 수(Integer)

__2 Result__

wiki_summ: 위키백과의 요약

summ_res: 블로그 내용들을 크롤링한 요약문 리스트

keywords: 블로그 요약에서 추출한 상위 키워드 리스트

cards: 네이버 관련 검색어 리스트

## Class
### KwordModule

#### toSummary(query, pnum, knum):

검색어(query)의 url들을 class WebTool.getLinks()로 추출. Google Search Results

같은 class의 getDocData() 함수와 추출한 url 리스트를 멀티 프로세싱을 사용하여, 본문 데이터 추출

키워드 추출(중복제거), 관련 검색어(네이버) 추출

위키 요약문, 일반 사이트 요약문, 중복 제거된 키워드 리스트, 관련 검색어를 반환

멀티 프로세싱의 효율은 컴퓨터 환경마다 다르므로, 아래 코드에서 한번에 처리할 프로세스의 개수를 조절한다

    multiprocess = Pool(11)
    


#### getDocData(url):

해당 url에서 HTML태그를 제거한 본문 텍스트를 추출하여, 요약문과 키워드 반환

### WebTool

#### getLinks(query, **kargs):

구글에서 해당 검색어의 url 리스트를 반환.

옵션으로 특정 사이트 검색(site="site:url"), 검색할 최대 페이지 수(max_pages="nums")를 줄 수 있음

#### parseText(url):

해당 url의 HTML 태그 중 본문 문자열만 반환한다.

본문 텍스트가 없을 시 빈 문자열 반환

#### def getRelated(query):

해당 검색어의 네이버 관련 검색어 리스트를 반환

### TextRank

TextRank 알고리즘으로 입력된 문장들간의 유사도를 계산, 중요도가 높은 순으로 요약문을 만들어 낸다.
