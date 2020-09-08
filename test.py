import json
import math
from nltk.corpus import wordnet as wn
from itertools import product

import SimUtil
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


main()
# for i in range(2,6):
#     cate = 'a'+ str(i)
#     for l in range(1,3):
#         num = 0
#         right_o = 0
#         right_s = 0
#         cate2 = 'b'+str(i)+str(l)
#         for j in range(1,6):
#             src = cate+ str(j)
#             if i==3 and j==4:
#                 continue
#             for k in range(1,6):
#                 if i == 3 and k == 4:
#                     continue
#                 if k != j:
#                     ref = cate+str(k)
#                     right_o+=howMuch('data/'+cate+'_'+cate2+'/'+src+'_'+ref+'_T.txt','data/'+cate+'_'+cate2+'/'+ref+'.json')
#                     # right_s += howMuch1('data/' + cate + '_' + cate2 + '/' + src + '_' + ref + '_T.txt',
#                     #                    'data/' + cate + '_' + cate2 + '/' + ref + '.json')
#                     num+=1
#         print(cate+cate2, right_o, num, right_o/num)


