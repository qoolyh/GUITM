import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import xml.etree.ElementTree as xeTree
#语料
# import ElemSim
#



def resolveJson(path):
    file = open(path, "rb")
    fileJson = json.load(file)
    resID = []
    resClass = []
    resText = []
    resContenDesc = []
    for fj in fileJson:
        text = fj["text"]
        content_desc = fj["content-desc"]
        activity = fj["activity"]
        evt_type = fj['event_type']
        res.append({'txt':text,'desc':content_desc,'act':activity,'etpe':evt_type})
    return res


def splitByUpper(str):
    res = []
    for k in str.split('_'):
        for s in k.split(' '):
            prev = 0
            flag = False
            for tmpS in s:
                if tmpS.isupper():
                    flag = True
                    tmp = s.find(tmpS)
                    if tmp != prev:
                        res.append(s[prev:tmp])
                        prev = tmp
            if flag:
                res.append(s[prev:len(s)])
            if not flag and not s.isspace() and s != '':
                res.append(s)
    return res


def parseTxt(res):
    txt = ''
    for i in res:
        tmp = i['txt']
        str = splitByUpper(tmp)
        for s in str:
            txt+=s+' '
            # id: 'a b c'
    return txt


def output():
    result1 = resolveJson(path)
    result2 = resolveJson(path2)
    print(parseTxt(result1))
    corpus = [
        parseTxt(result1), parseTxt(result2)
    ]
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    word = vectorizer.get_feature_names()
    print(word)
    print(cosine_similarity(X.toarray()))




path = r"F:\graduate\TestFlow\code-release\code-release\test_repo\a3\b31\base\a31.json"
path2 = r"F:\graduate\TestFlow\code-release\code-release\test_repo\a3\b31\base\a33.json"
output()