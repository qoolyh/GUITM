import json

from Parser_STL import test_to_STL
from Parser_me import parseJson2STG

ans = {}


def get_input(STL: list):
    res = {}
    ipt = [] #edges
    for i in range(len(STL)):
        state = STL[i]
        curr = {}
        curr.update({'ipts':[]})
        curr.update({'next': []})
        edge = state.edges
        has_ipt = False
        for e in edge:
            if e['isInput']:
                curr['ipts'].append(e)
                has_ipt = True
        if has_ipt:
            curr.update({'idx':i})
            ipt.append(curr)
    for i in range(len(ipt)-1,0,-1):
        prev = i-1
        if prev != -1:
            if ipt[i]['idx']-1 == ipt[prev]['idx']:
                ipt[prev]['next'].append(ipt[i])
    record = []
    for i in range(len(ipt)):
        next = i+1
        curr = i
        if i == 0:
            record.append(i)
        if next < len(ipt):
            if ipt[next]['idx'] != ipt[curr]['idx']+1 and i!=0:
                record.append(i)
            while(ipt[next]['idx'] == ipt[curr]['idx']+1):
                ipt[i]['ipts'].extend(ipt[next]['ipts'])
                curr +=1
                next +=1
                if next >= len(ipt):
                    break
            i = curr
    for i in record:
        res.update({ipt[i]['ipts'][0]['activity']:ipt[i]})
    #
    #
    #     if next < len(ipt):
    #         if ipt[next]['idx'] == ipt[i]['idx']+1:
    #             ipt[i]['ipts'].extend(ipt[next]['ipts'])
    # for i in ipt:
    #     curr = i
    #     if len(ipt[i]['next'])>0:
    #         next =
    #     res.update({i['ipts'][0]['activity']:i})
    return res


# def input_matcher(ipt: list, STG: list):
#     stl = []
#     for i in ipt:
#         for t_i in STG:
#             if
#     return stl


def similar(ipt: object, tgt: object):
    same = False
    edgesets = tgt.edges
    for edge in edgesets:
        if len(edge)>1:
            res = ipt_match_help(ipt, edge)
    return same


def ipt_match_help(ipt, edge):
    ipts = ipt
    use_next = 0
    flag = len(ipt)>=len(edge)-1
    if len(ipt)<len(edge)-1:
        if len(ipt['next'])>0:
            nexts = ipt['next']
            left = len(edge)-1-len(ipt)
            for next in nexts:
                if left > len(next):
                    left-=len(next)
                    use_next += 1
                else:
                    flag = True
                    break
            if left>0:
                flag = False
                return []
    if flag:
        curr = ipt
        for count in range(use_next):
            next = curr['next']
            ipts.extend(next)
            curr = next
    return ipts


def getAnswer(ori):
    res = {}
    for e in ori:
        if e.__contains__('action'):
            if 'send_keys' in e['action'][0]:
                act = e['activity']
                if res.__contains__(act):
                    res[act].append(e['action'][1])
                else:
                    oneact = {act:[e['action'][1]]}
                    res.update(oneact)
    return res1
#
#
# print(getAnswer('data/a3_b31/a31.json'))
test_json = 'data/a3_b31/a35.json'
file = open(test_json, "rb")
test = json.load(file)
sdir = 'data/a3_b31/tar/a35/activitiesSummary.json'
sg = parseJson2STG(sdir)
STL = test_to_STL(test, sg)
res = get_input(STL)
for k in res:
    print(k)
    for n in res[k]['ipts']:
        print(n)
