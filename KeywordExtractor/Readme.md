# KeywordExtractor

�˻��� ��α׵��� ��๮, Ű���� ����, ��Ƽ ���μ������� ó��

## Dependency Package:
BeautifulSoup

urllib

requests

konlpy

networkx

## How to use:

    kmodule = KwordModule()

    wiki_summ, summ_res, keywords, cards = kmodule.toSummary("����ž", 10, 15)

__1 Parameter:__

�˻��� Ű����(String)

����� ���� ��(Integer)

������ Ű���� ��(Integer)

__2 Result__

wiki_summ: ��Ű����� ���

summ_res: ��α� ������� ũ�Ѹ��� ��๮ ����Ʈ

keywords: ��α� ��࿡�� ������ ���� Ű���� ����Ʈ

cards: ���̹� ���� �˻��� ����Ʈ

## Class
### KwordModule

#### toSummary(query, pnum, knum):

�˻���(query)�� url���� class WebTool.getLinks()�� ����. Google Search Results

���� class�� getDocData() �Լ��� ������ url ����Ʈ�� ��Ƽ ���μ����� ����Ͽ�, ���� ������ ����

Ű���� ����(�ߺ�����), ���� �˻���(���̹�) ����

��Ű ��๮, �Ϲ� ����Ʈ ��๮, �ߺ� ���ŵ� Ű���� ����Ʈ, ���� �˻�� ��ȯ

��Ƽ ���μ����� ȿ���� ��ǻ�� ȯ�渶�� �ٸ��Ƿ�, �Ʒ� �ڵ忡�� �ѹ��� ó���� ���μ����� ������ �����Ѵ�

    multiprocess = Pool(11)
    


#### getDocData(url):

�ش� url���� HTML�±׸� ������ ���� �ؽ�Ʈ�� �����Ͽ�, ��๮�� Ű���� ��ȯ

### WebTool

#### getLinks(query, **kargs):

���ۿ��� �ش� �˻����� url ����Ʈ�� ��ȯ.

�ɼ����� Ư�� ����Ʈ �˻�(site="site:url"), �˻��� �ִ� ������ ��(max_pages="nums")�� �� �� ����

#### parseText(url):

�ش� url�� HTML �±� �� ���� ���ڿ��� ��ȯ�Ѵ�.

���� �ؽ�Ʈ�� ���� �� �� ���ڿ� ��ȯ

#### def getRelated(query):

�ش� �˻����� ���̹� ���� �˻��� ����Ʈ�� ��ȯ

### TextRank

TextRank �˰������� �Էµ� ����鰣�� ���絵�� ���, �߿䵵�� ���� ������ ��๮�� ����� ����.
