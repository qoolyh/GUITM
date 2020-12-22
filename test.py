import json
import math
from nltk.corpus import wordnet as wn
from itertools import product

import SimUtil
import simCal
from Parser_me import parseJson2STG
from StrUtil import StrUtil
from ElemSim import arraySim
from Parser_STL import json_to_STG
from Parser_STL import test_to_STL
import time
def json2array(jsonDir):
    array = []
    file = open(jsonDir, "rb")
    j = json.load(file)
    for i in j:
        array.append(i)
    return array


def howMuch1(tgt, gnd):
    # get the previous action of the last oracle
    s,o = getS(gnd)
    if haveEdge(tgt, s):
        return 1
    else:
        return 0


def howMuch(tgt, gnd):
    # get the previous action of the last oracle
    s,o= getS(gnd)
    if haveEdge1(tgt, o):
        return 1
    else:
        return 0



def getS(json):
    array = json2array(json)
    l = len(array) -1
    return array[l-1],array[l]


def haveEdge1(tgt, s):
    with open(tgt, encoding="utf-8") as f:
        lines = f.readlines()
        idx = 0
        str = ''
        for l in lines:
            if l.find('----time')!=-1:
                str = lines[idx-2]
                break
            idx+=1
        str = str.strip()
        str = str[0:len(str)-1]
        v = s['activity'].strip()
        v = v[0:len(v)-1]
        return str == v


def haveEdge(tgt, s):
    with open(tgt, encoding="utf-8") as f:
        lines = f.readlines()
        idx = 0
        str = ''
        for l in lines:
            if l.find('----time')!=-1:
                str = lines[idx-5]
                break
            idx+=1
        # str = str.strip()
        # str = str[0:len(str)-1]
        # v = s['activity'].strip()
        # v = v[0:len(v)-1]
        # print(str, v)
        return str.strip() == s['activity'].strip()
        # return str == v

def main():
    src = 'data/a2_b22/src/a22/activitiesSummary.json'
    t = 'data/a2_b22/a22.json'
    SRC = json_to_STG(src)
    file = open(t, "rb")
    test = json.load(file)
    STL = test_to_STL(test, SRC)
    for state in STL:
        print(len(state.edges))
        print(state.act)
        if hasattr(state,'oracle'):
            print('oracle.....', state.oracle)
            print('istext....', state.oracle['isTxt'], state.oracle['oTxt'])
            print('isElem....', state.oracle['isElem'])
        print('-----------')
        if hasattr(state,'bind_to'):
            print('bind----------', state.bind_to)

    # str1 = 'menu_profile_name'
    # str2 = 'Config_Menu_NAME'
    # dis = SimUtil.arraySim(StrUtil.tokenize("resource-id", str1), StrUtil.tokenize("resource-id", str2))
    # print(dis)


def testGSim_tf(sg, tg):
    res = {}
    tmp = {}
    score = []
    for si in sg:
        for ti in tg:
            s_graph = sg[si].elements
            t_graph = tg[ti].elements
            v = simCal.graphSim_TFIDF(s_graph, t_graph)
            if res.__contains__(v):
                res[v].append({si:ti})
            else:
                res.update({v:[{si:ti}]})
                score.append(v)
    score.sort(reverse=True)
    for s in score:
        tmp.update({s:res[s]})
    return tmp


def testGSim_w2v(sg, tg):
    res = {}
    tmp = {}
    score = []
    for si in sg:
        for ti in tg:
            s_graph = sg[si].elements
            t_graph = tg[ti].elements
            v = simCal.graphSim_W2V(s_graph, t_graph)
            if res.__contains__(v):
                res[v].append({si:ti})
            else:
                res.update({v:[{si:ti}]})
                score.append(v)
    score.sort(reverse=True)
    for s in score:
        tmp.update({s:res[s]})
    return tmp



sdir = 'data/a3_b31/tar/a31/activitiesSummary.json'
tdir = 'data/a3_b31/tar/a35/activitiesSummary.json'
sg = parseJson2STG(sdir)
tg = parseJson2STG(tdir)
for si in sg:
    if 'CreateAccountActivity' in si:
        for ti in tg:
            v = simCal.gSim_baseline(sg[si].elements, tg[ti].elements)
            print(si, ti)
            print(v)
        break

#
# res = testGSim_w2v(sg,tg)
# for v in res:
#     print('__________', v)
#     print(res[v])




