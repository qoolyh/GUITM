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
