import json

ans = {}
def get_input(STL: list):
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
    return ipt


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


def ipt_match_help(ipt, edge, tgtName):
    res = {}
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
                return res
    if flag:
        ipts = ipt
        curr = ipt
        for count in range(use_next):
            next = curr['next']
            ipts.extend(next)
            curr = next
        for i in ipts:
            text = i['action'][1]
            for ipt_t in edge:
                if ipt_t['type'] == 'input':
                    key = ipt_t['resource-id']
                    if ans[tgtName][key] == ipt_t['text']:
                        res.update({ipt['idx']:ipt_t})
                        break
    return res


# def getAnswer(dir):
#     res = {}
#     file = open(dir, 'rb')
#     ori = json.load(file)
#     for e in ori:
#         if 'send_keys' in e['action'][0]:
#             res.update({e['resource-id']:e['action'][1]})
#     return res
#
#
# print(getAnswer('data/a3_b31/a31.json'))