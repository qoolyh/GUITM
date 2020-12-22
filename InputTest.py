import copy
import json
import re

from Parser_me import parseJson2STG
from simCal import single_elem_sim

ANS = {}

def exhaustive_search(ipts: list, edges: list):
    res = {}
    map = sort_by_Graph_sim(ipts, edges)
    for i in ipts:
        ipt = ipts[i]
        tgt = edges[map[i]]
        sorted_ipt = priority_rank_A(ipt, tgt)
        for comp in sorted_ipt:
            if check(comp, tgt):
                if not res.__contains__(map[i]):
                    res.update({map[i]:comp})
                break
    return res


# def sort_by_graph_sim(src, tgt):
#     for s in src:
#         for t in tgt:


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
            if len(elements)>1:
                for e in elements:
                    if isinstance(e,list):
                        tmp_e = []
                        for k in e:
                            if k['type'] == 'input':
                                tmp_e.append(k)
                        if len(tmp_e)>1:
                            egs.append(tmp_e)
                    else:
                        if e['type'] == 'input':
                            tmp.append(e)
            if len(tmp)>0:
                egs.append(tmp)
        if len(egs)>0:
            iptEdge.update({key:egs})
    return iptEdge


def check(ipt_comb, ans):
    correct = True
    key = ''
    for i in range(len(ipt_comb)):
        if ipt_comb[i]['text'] == ans[i]:
            continue
        else:
            correct = False
            break
    return correct


def A(array,  n): # return A(len(array),n)
    comp = []
    if n == 0:
        return comp
    for i in range(len(array)):
        copy_array = copy.deepcopy(array)
        copy_array.pop(i)
        left = A(copy_array, n-1)
        if len(left)==0:
            comp.append([array[i]])
        else:
            for k in left:
                new_comp_k = [array[i]]
                new_comp_k.extend(k)
                comp.append(new_comp_k)
    return comp


def priority_rank_A(ipt, edge):
    comp = []
    if len(edge) == 0:
        return comp
    ranked_ipt = rank(ipt, edge[0])
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


def rank(ipt, target):
    ranked_ipt = []
    score2ipt = {}
    scores = []
    for i in ipt:
        score = single_elem_sim(i, target)
        print(score, i['resource-id'])
        if score2ipt.__contains__(score):
            score2ipt[score].append(i)
        else:
            score2ipt.update({score:[i]})
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
            U





ipt_p = 'data/a3_b31/a31.json'
tgt_p = 'data/a3_b31/a32.json'
# ans = getAnswer(tgt_p)
ipt_file = open(ipt_p, "rb")
ipts = json.load(ipt_file)
ipt_file.close()
tgt_file = open(tgt_p, "rb")
tgts = json.load(tgt_file)
tgt_file.close()
STG = parseJson2STG('data/a3_b31/tar/a32/activitiesSummary.json')

ipt = []
tgt = []
egs = getInputEdges(STG)
for eg in egs:
    print(egs[eg])


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