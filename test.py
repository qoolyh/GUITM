import json
import math
from nltk.corpus import wordnet as wn
from itertools import product

import Parser_STL
import Parser_me
import SimUtil
import Util
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
    src = 'data/a3_b31/src/a31/activitiesSummary.json'
    start = 'com.contextlogic.wish.activity.login.createaccount.CreateAccountActivity0'
    end = 'com.contextlogic.wish.activity.login.createaccount.CreateAccountActivity0'
    sg = Parser_me.parseJson2STG(src)
    edges = Util.getPath(sg[start], sg[end], [])
    print(edges)



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



main()

#
# sdir = 'data/a3_b31/tar/a31/activitiesSummary.json'
# tdir = 'data/a3_b31/tar/a35/activitiesSummary.json'
# sg = parseJson2STG(sdir)
# tg = parseJson2STG(tdir)
# for si in sg:
#     if 'CreateAccountActivity' in si:
#         for ti in tg:
#             v = simCal.gSim_baseline(sg[si].elements, tg[ti].elements)
#             print(si, ti)
#             print(v)
#         break
#
#
# res = testGSim_w2v(sg,tg)
# for v in res:
#     print('__________', v)
#     print(res[v])




