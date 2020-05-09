import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import xml.etree.ElementTree as xeTree
import os
from StrUtil import StrUtil
import gensim
#语料
# import ElemSim
#

model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit= 500000)

def w2v_sim(w_from, w_to):
    # w_from = "".join(list(filter(str.isalpha, w_from)))
    # w_to = "".join(list(filter(str.isalpha, w_to)))
    if w_from.lower() == w_to.lower():
        sim = 1.0
    elif w_from in model.vocab and w_to in model.vocab:
        sim = model.similarity(w1=w_from, w2=w_to)
    else:
        sim = 0
    return sim

def arraySim(strArray, strArray2):
    scores = []
    # valid_new_words = []
    # valid_old_words = copy.deepcopy(strArray2)
    valid_new_words = set()
    valid_old_words = set(strArray2)

    for s1 in strArray:
        for s2 in strArray2:
            sim = w2v_sim(s1, s2)
            if sim:
                valid_new_words.add(s1)
                scores.append((s1, s2, sim))
    scores = sorted(scores, key=lambda x: x[2], reverse=True)
    counted = []
    for new_word, old_word, score in scores:
        if new_word in valid_new_words and old_word in valid_old_words:
            valid_new_words.remove(new_word)
            valid_old_words.remove(old_word)
            counted.append(score)
        if not valid_new_words or not valid_old_words:
            break
    # return sum(counted) / len(strArray) if strArray else 0
    return sum(counted) / len(counted) if counted else 0

def walkData(rootNode, elementsList):
    elementsList.append(rootNode.attrib)
    for childNode in rootNode:
        walkData(childNode, elementsList)

def resolveJson(path):

    elementsList = []
    xml_tree = xeTree.ElementTree(file=path)  # 文件路径
    root = xml_tree.getroot()
    for child in root:
        walkData(child, elementsList)
    # file = open(path, "rb")
    # fileJson = json.load(file)
    resID = []
    resClass = []
    resText = []
    resContenDesc = []
    for ele in elementsList:
        text = ele["text"]
        content_desc = ele["content-desc"]
        resource_id = ele["resource-id"] if ele["resource-id"].find("/") == -1 else ele["resource-id"].split('/')[1]
        resource_class = ele['class'].split('.')[-1:][0]
        resText.append({'txt':text})
        resID.append({'txt':resource_id})
        resClass.append({'txt':resource_class})
        resContenDesc.append({'txt':content_desc})
    # print(resClass)
    # print(resID)
    return resID, resClass, resText, resContenDesc


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

def graphSim_W2V(src_elems, tar_elems):
    resID1 = ""
    resClass1 = ""
    resText1 = ""
    resContenDesc1 = ""
    for ele in src_elems:
        text = ele.text
        content_desc = ele.desc
        resource_class = ele.cls.split('.')[-1:][0]
        resource_id = ele.id if ele.id.find("/") == -1 else ele.id.split('/')[1]
        resource_id = "_".join(
            StrUtil.expand_text(resource_class, "resource-id", StrUtil.tokenize("resource-id", resource_id)))

        resText1 += " " + text
        resID1 += "_" + resource_id
        resClass1 += " " + resource_class
        resContenDesc1 += " " + content_desc

    resID2 = ""
    resClass2 = ""
    resText2 = ""
    resContenDesc2 = ""
    for ele in tar_elems:
        text = ele.text
        content_desc = ele.desc
        resource_class = ele.cls.split('.')[-1:][0]
        resource_id = ele.id if ele.id.find("/") == -1 else ele.id.split('/')[1]
        resource_id = "_".join(
            StrUtil.expand_text(resource_class, "resource-id", StrUtil.tokenize("resource-id", resource_id)))

        resText2 += " " + text
        resID2 += "_" + resource_id
        resClass2 += " " + resource_class
        resContenDesc2 += " " + content_desc

    idScore = arraySim(StrUtil.tokenize("resource-id", resID2), StrUtil.tokenize("resource-id", resID1))
    textScore = arraySim(StrUtil.tokenize("text", resText2), StrUtil.tokenize("text", resText2))
    descScore = arraySim(StrUtil.tokenize("content-desc", resContenDesc2), StrUtil.tokenize("content-desc", resContenDesc1))

    return (idScore + textScore + descScore) / 3

def graphSim_TFIDF(src_elems, tar_elems):
    # return 0.0001
    resID1 = []
    resClass1 = []
    resText1 = []
    resContenDesc1 = []
    for ele in src_elems:
        text = ele.text
        content_desc = ele.desc
        resource_id = ele.id if ele.id.find("/") == -1 else ele.id.split('/')[1]
        resource_class = ele.cls.split('.')[-1:][0]
        resText1.append({'txt': text})
        resID1.append({'txt': resource_id})
        resClass1.append({'txt': resource_class})
        resContenDesc1.append({'txt': content_desc})
    resID2 = []
    resClass2 = []
    resText2 = []
    resContenDesc2 = []
    for ele in tar_elems:
        text = ele.text
        content_desc = ele.desc
        resource_id = ele.id if ele.id.find("/") == -1 else ele.id.split('/')[1]
        resource_class = ele.cls.split('.')[-1:][0]
        resText2.append({'txt': text})
        resID2.append({'txt': resource_id})
        resClass2.append({'txt': resource_class})
        resContenDesc2.append({'txt': content_desc})

    tempSimSet = {}
    corpusID = [
        parseTxt(resID1), parseTxt(resID2)
    ]
    if corpusID == ['', '']:
        tempSimSet["IDSim"] = 0
    else:
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(corpusID)
        word = vectorizer.get_feature_names()
        # print(word)
        # print("ID: " ,cosine_similarity(X.toarray())[0][1])
        tempSimSet["IDSim"] = cosine_similarity(X.toarray())[0][1]

    corpusClass = [
        parseTxt(resClass1), parseTxt(resClass2)
    ]
    if corpusClass == ['', '']:
        tempSimSet["ClassSim"] = 0
    else:
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(corpusClass)
        word = vectorizer.get_feature_names()
        # print(word)
        # print("Class: ",cosine_similarity(X.toarray())[0][1])
        tempSimSet["ClassSim"] = cosine_similarity(X.toarray())[0][1]

    corpusText = [
        parseTxt(resText1), parseTxt(resText2)
    ]
    # print(corpusText)
    if corpusText == ['', '']:
        tempSimSet["TextSim"] = 0
    try:
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(corpusText)
        word = vectorizer.get_feature_names()
        # print(word)
        # print("Text: ",cosine_similarity(X.toarray()))
        tempSimSet["TextSim"] = cosine_similarity(X.toarray())[0][1]
    except Exception as e:
        tempSimSet["TextSim"] = 0

    corpusConentDesc = [
        parseTxt(resContenDesc1), parseTxt(resContenDesc2)
    ]
    if corpusConentDesc == ['', '']:
        tempSimSet["ContentDescSim"] = 0
    else:
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(corpusConentDesc)
        word = vectorizer.get_feature_names()
        # print(word)
        # print("ContentDesc: ",cosine_similarity(X.toarray()))
        tempSimSet["ContentDescSim"] = cosine_similarity(X.toarray())[0][1]
    # if tempSimSet["IDSim"] <= 0.1 and tempSimSet["TextSim"] <= 0.1:
    #     return 0
    return (tempSimSet["IDSim"] + tempSimSet["TextSim"] + tempSimSet["ContentDescSim"]) / 3



def getFileName(path, ends):
    F = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == ends:
                # t = os.path.splitext(file)[0]
                t = file
                F.append(t)
    return F

def getFileDir(path):
    ds = []
    for root, dirs, files in os.walk(path):
        for d in dirs:
            ds.append(d)
    return d