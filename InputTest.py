import copy
import json
import re

from numpy.core.defchararray import isnumeric

from StrUtil import StrUtil
import simCal
from InputGenerator import get_input, getAnswer
from Parser_STL import test_to_STL
from Parser_me import parseJson2STG
from simCal import single_elem_sim

ANS = {}


# def exhaustive_search(ipts: list, edges: list):
#     res = {}
#     map = sort_by_Graph_sim(ipts, edges)
#     for i in ipts:
#         ipt = ipts[i]
#         tgt = edges[map[i]]
#         sorted_ipt = priority_rank_A(ipt, tgt)
#         for comp in sorted_ipt:
#             if check(comp, tgt):
#                 if not res.__contains__(map[i]):
#                     res.update({map[i]:comp})
#                 break
#     return res


def exhaustive_search(SRC_ipts, TGT_ipts, ans, SRC, TGT):
    res = {}
    map = sort_by_graph_sim(SRC_ipts, TGT_ipts, SRC, TGT, ans)
    for i in SRC_ipts:
        look_forward = 0
        ipt = SRC_ipts[i]
        tgts = map[i]
        for tgt in tgts:
            use_next = 0
            if tgt not in ans:
                continue
            sorted_ipt = priority_rank_A(ipt['ipts'], TGT_ipts[tgt])
            print('comparing to ', tgt, len(sorted_ipt))
            for comp in sorted_ipt:
                if check(comp, ans[tgt]):
                    if tgt not in res:
                        res.update({tgt: comp})
                        look_forward += 1
                    if look_forward > 3:
                        break  # once you break, no more tgts will be matched
    return res


def sort_by_graph_sim(SRC_ipts, TGT_ipts, SRC, TGT, ans):
    # return gsim({si: [tj, tj+1]}, {si+1: [tk,tk+1]}...)
    gsim_Ranked = {}
    counter = 1
    for s in SRC_ipts:
        si = {}
        score = []
        tmp = []
        tcounter = 1
        for t in TGT_ipts:
            if t not in ans:
                tcounter += 1
                continue
            src_i = SRC[s]
            tgt_i = TGT[t]
            gsim_i = simCal.gSim_baseline(src_i.elements, tgt_i.elements)
            if si.__contains__(gsim_i):
                si[gsim_i].append(t)
            else:
                si.update({gsim_i: [t]})
                score.append(gsim_i)
            tcounter += 1
        score.sort(reverse=True)
        for k in score:
            tmp.extend(si[k])
        gsim_Ranked.update({s: tmp})
        counter += 1
    return gsim_Ranked


def getInputEdges(STG):
    iptEdge = {}
    for s in STG:
        state = STG[s]
        key = s
        path = state.edges
        egs = []
        for edges in path:
            tmp = []
            elements = edges.target
            if len(elements) > 1:
                for e in elements:
                    if isinstance(e, list):
                        tmp_e = []
                        for k in e:
                            if k['type'] == 'input':
                                tmp_e.append(k)
                        if len(tmp_e) > 1:
                            egs.append(tmp_e)
                    else:
                        if e['type'] == 'input':
                            tmp.append(e)
            if len(tmp) > 0:
                egs.append(tmp)
        if len(egs) > 0:
            iptEdge.update({key: egs})
    return iptEdge


def get_input_from_STG(STG):
    ipts = {}
    for s in STG:
        iptElem = []
        state = STG[s]
        key = s
        path = state.edges
        egs = []
        for edges in path:
            elements = edges.target
            if len(elements) > 1:
                for e in elements:
                    if isinstance(e, list):
                        tmp_e = []
                        for k in e:
                            if k['type'] == 'input':
                                if k not in iptElem:
                                    iptElem.append(k)
                    else:
                        if e['type'] == 'input':
                            if e not in iptElem:
                                iptElem.append(e)
        if len(iptElem) > 0:
            ipts.update({key: iptElem})
    return ipts


def check(ipt_comb, ans):
    correct = True
    key = ''
    ipt_words = []
    for i in range(len(ipt_comb)):
        if '.net' in ipt_comb[i]['action'][1]:
            if '.net' in ans[i]:
                continue
            else:
                correct = False
                break
        if ipt_comb[i]['action'][1] == ans[i] or ans[i] == '666':
            continue
        else:
            correct = False
            break
    return correct


def A(array, n):  # return A(len(array),n)
    comp = []
    if n == 0:
        return comp
    for i in range(len(array)):
        copy_array = copy.deepcopy(array)
        copy_array.pop(i)
        left = A(copy_array, n - 1)
        if len(left) == 0:
            comp.append([array[i]])
        else:
            for k in left:
                new_comp_k = [array[i]]
                new_comp_k.extend(k)
                comp.append(new_comp_k)
    return comp


def priority_rank_A(ipts, edge):
    comp = []
    if len(edge) == 0:
        return comp
    ranked_ipt = rank(ipts, edge[0])
    for i in range(len(ranked_ipt)):
        copy_ipt = copy.deepcopy(ranked_ipt)
        copy_ipt.pop(i)
        copy_edge = copy.deepcopy(edge)
        copy_edge.pop(0)
        left = priority_rank_A(copy_ipt, copy_edge)
        if len(left) == 0:
            comp.append([ranked_ipt[i]])
        else:
            for k in left:
                new_comp_k = [ranked_ipt[i]]
                new_comp_k.extend(k)
                comp.append(new_comp_k)
    return comp


def rank(ipts, target):
    ranked_ipt = []
    score2ipt = {}
    scores = []
    for i in ipts:
        score = single_elem_sim(i, target)
        if score2ipt.__contains__(score):
            score2ipt[score].append(i)
        else:
            score2ipt.update({score: [i]})
            scores.append(score)
    scores.sort(reverse=True)
    for s in scores:
        ranked_ipt.extend(score2ipt[s])
    return ranked_ipt


# graph_p = 'data/a1_b11/tar/a15/activitiesSummary.json'
# graphs = parseJson2STG(graph_p)
# for k in graphs:
#     graph = graphs[k]
#     print(id_format(graph))
#     break

def test_gsim(src, tgt):
    s_g = parseJson2STG('data/a3_b31/tar/a31/activitiesSummary.json')
    t_g = parseJson2STG('data/a3_b31/tar/a32/activitiesSummary.json')
    for sg in s_g:
        for tg in t_g:
            s_graph = s_g[sg]
            t_graph = t_g[tg]


def main():
    cate = '5'
    folder = 'a' + cate + '_b' + cate + '1'
    src = 'a' + cate + '1'
    ref = 'a' + cate + '2'

    sdir = 'data/' + folder + '/tar/' + src + '/activitiesSummary.json'
    tdir = 'data/' + folder + '/tar/' + ref + '/activitiesSummary.json'
    test_json = 'data/' + folder + '/' + src + '.json'
    ansjson = 'data/' + folder + '/' + ref + '.json'
    sg = parseJson2STG(sdir)
    tg = parseJson2STG(tdir)
    file = open(test_json, "rb")
    test = json.load(file)

    file2 = open(ansjson, "rb")
    ansf = json.load(file2)
    STL = test_to_STL(test, sg)
    oracle_binding(STL)
    # tipt = get_input_from_STG(tg)
    # sipt = get_input(STL)
    # ans = getAnswer(ansf)
    # print(ans)
    # res = exhaustive_search(sipt,tipt, ans, sg, tg)
    # for r in res:
    #     print(r)
    #     print(res[r])


def oracle_binding(STL):
    oracles = []
    for s in STL:
        if hasattr(s, 'oracle'):
            oracles.append(s.oracle)
    STL_ipts = get_input(STL)
    for o in oracles:
        o_text = o['text']
        o_desc = o['content-desc']
        o_content = o_text + ' ' + o_desc
        for act in STL_ipts:
            ipts = STL_ipts[act]['ipts']
            for i in ipts:
                if isnumeric(o_text) and isnumeric(i['action'][1]):
                    print(i['action'][1], o_content)
                text = i['text'] + ' ' + i['action'][1]
                if similar_substr(text, o_content):
                    print(text, o_content)


def similar_substr(text, o_content):
    tk1 = StrUtil.tokenize('text', text)
    tk2 = StrUtil.tokenize('text', o_content)
    same = False
    for t1 in tk1:
        for t2 in tk2:
            if t1 == t2:
                return True
    return same


def isNum(s):
    if isnumeric(s):
        return True
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False


# main()

print(isNum('+1.300'))

# for si in sg:
#     if 'CreateAccountActivity' in si:
#         for ti in tg:
#             v = simCal.gSim_baseline(sg[si].elements, tg[ti].elements)
#             print(si, ti)
#             print(v)
#         break


# ipt_p = 'data/a3_b31/a31.json'
# tgt_p = 'data/a3_b31/a32.json'
# # ans = getAnswer(tgt_p)
# ipt_file = open(ipt_p, "rb")
# ipts = json.load(ipt_file)
# ipt_file.close()
# tgt_file = open(tgt_p, "rb")
# tgts = json.load(tgt_file)
# tgt_file.close()
# STG = parseJson2STG('data/a3_b31/tar/a32/activitiesSummary.json')
#
# ipt = []
# tgt = []
# egs = getInputEdges(STG)
# for eg in egs:
#     print(egs[eg])


# for i in ipts:
#     if 'send_keys' in i['action'][0]:
#         ipt.append(i)
# for i in tgts:
#     if 'send_keys' in i['action'][0]:
#         tgt.append(i)
#
# res = priority_rank_A(ipt, [tgt[1]])
# for r in res:
#     print(r)
# print(res)
