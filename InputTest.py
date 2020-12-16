import copy

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
    for i in ipt:
        score = w2vSim(i, target)
        score2ipt
    return ranked_ipt