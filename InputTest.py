import copy
import re

from Parser_me import parseJson2STG
from simCal import single_elem_sim

ANS = {}

def exhaustive_search(ipts: list, edges: list):
    res = []

    return res


def check(ipt_comb, ipts):
    correct = True
    key = ''
    for i in ipts:
        key+=ipts['activity']
    ans = ANS[key]
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
        if score2ipt.__contains__(score):
            score2ipt[score].append(i)
        else:
            score2ipt.update({score:i})
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




def ranktest(sim):
    ranked_ipt = []
    score2ipt = {}
    scores = []
    ipt= ['a','b','c','d','e']
    target = ['A','B','C','D','E']
    for i in range(len(ipt)):
        score = sim[i][1]
        print(score)
        if score2ipt.__contains__(score):
            score2ipt[score].append(ipt[i])
        else:
            score2ipt.update({score: [ipt[i]]})
            scores.append(score)
    scores.sort(reverse=True)
    for s in scores:
        ranked_ipt.extend(score2ipt[s])
    return ranked_ipt


sim = [[5,4,3,2,1],[1,2,3,4,5],[3,4,5,2,1],[4,5,3,2,1],[3,3,4,5,6]]
res = ranktest(sim)
print(res)