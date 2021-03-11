import json
from copy import deepcopy

import Parser_me
from Edge import Edge
from Element import Element
from Graph import Graph
from Util import find_out


def json_to_STG(jsonPath):  # format: activity: graph_obj
    graphs = {}
    # file = open(jsonPath, "rb")
    file = open(jsonPath)
    acts = json.load(file)
    gidx = 0
    for actName in acts:
        act = acts[actName]
        elems = act['elements']
        edges = act['edge']
        eIdx = 0
        edgIdx = 0
        edgArray = []
        elemArray = []
        for e in elems:
            id = e['resource-id']
            cls = e['class']
            desc = e['content-desc']
            text = e['text']
            checkable = e['checkable']
            checked = e['checked']
            clickable = e['clickable']
            focusable = e['focusable']
            scrollable = e['scrollable']
            longClickable = e['long-clickable']
            password = e['password']
            bounds = e['bounds']
            idx = str(gidx) + '_' + str(eIdx)
            tmp = Element(idx, id, cls, text, desc, checkable, checked, clickable, focusable, scrollable, longClickable,
                          password, bounds, actName)
            eIdx += 1
            elemArray.append(tmp)

        for edg in edges:
            fromGraph = edg['from']
            toGraph = edg['to']
            target = edg['elements']
            event = 'click'
            tmpEdge = Edge(target, event, fromGraph, toGraph)
            edgArray.append(tmpEdge)
            edgIdx += 1

        tmpG = Graph(gidx, elemArray, edgArray)
        tmpG.act = actName
        graphs.update({actName: tmpG})
        gidx += 1
    return graphs


def test_to_STL(test, SRC):
    STL = []
    acts = {}
    idx = 0
    for t in test:
        t['idx'] = idx
        act = t['activity']
        state = deepcopy(SRC[act])
        t['isInput'] = ('send_keys' in t['action'][0])
        if t['event_type'] == 'oracle':
            t['isElem'] = 'element' in t['action'][0]
            t['isTxt'] = 'text' in t['action'][0]
            if act in acts:
                i = acts['act'][-1]
                t['disappear'] = 'invisible' in t['action'][0]
                if t['disappear']:
                    o_bind = trace_back(STL, t, len(STL) - 1)
                    t['trace_back'] = o_bind
                STL[i].oracle = t
            else:
                state.edges = []
                state.oracle = t
                STL.append(state)
        elif t['event_type'] == 'gui':
            if act == STL[-1].act: # continuous inputs
                STL[-1].edges.append(t)
            else:
                state.edges = [t]
                STL.append(state)
        elif t['event_type'] == 'SYS_EVENT':
            act = STL[-1 - 1].act
            state = deepcopy(SRC[act])
            state.edges = [t]
            STL.append(state)
        else:
            case4 = 0
        idx+=1
    update_bind(STL)
    return STL


# def test_to_STL(test, SRC):
#     STL = []
#     oracle = []
#     idx = 0
#     for t in test:
#         t['idx'] = idx
#         idx+=1
#         last = len(STL)-1
#         if t['event_type'] == 'gui':
#             t['isInput'] = ('send_keys' in t['action'][0])
#             act = t['activity']
#             state = deepcopy(SRC[act])
#             if not STL:
#                 state.edges = [t]
#                 STL.append(state)
#             else:
#                 if act == STL[last].act:
#                     STL[last].edges.append(t)
#                 else:
#                     state.edges = [t]
#                     STL.append(state)
#         elif t['event_type'] == 'SYS_EVENT':
#             act = STL[last-1].act
#             state = deepcopy(SRC[act])
#             state.edges = [t]
#             STL.append(state)
#         else: # in case of oracle
#             if not STL:
#                 continue
#             if t.__contains__('activity'):
#                 t['isElem'] = 'element' in t['action'][0]
#                 t['isTxt'] = 'text' in t['action'][0]
#                 t['oTxt'] = t['action'][3] if t['isTxt'] else ''
#                 t['disappear'] = 'invisible' in t['action'][0]
#                 if t['disappear']:
#                     o_bind = trace_back(STL,t,len(STL)-1)
#                     t['trace_back'] = o_bind
#                 act = t['activity']
#                 if act == STL[last].act:
#                     STL[last].oracle = t
#                 else:
#                     oracle = t
#                     if idx == len(test):
#                         state = deepcopy(SRC[act])
#                         state.oracle = oracle
#                         state.edges = []
#                         STL.append(state)
#             else:
#                 STL[last].oracle = t
#     update_bind(STL)
#     return STL


def update_bind(STL):
    for i in range(0, len(STL)):
        state = STL[i]
        if len(state.edges) > 1:
            inputs = state.edges[0:len(state.edges) - 1]
            for ipt in inputs:
                exist, idx = find_in_STL(ipt['action'][1], STL, i + 1)
                if exist:
                    STL[i].IObind_to = idx
                    STL[idx].IObind_from = i


def find_in_STL(text, STL, idx):
    for i in range(idx, len(STL)):
        if find_out(text, STL[i]):
            return True, i
    return False, -1


def trace_back(STL, t, idx):
    find = False
    for element in STL[idx].elements:
        if t['isTxt'] and element.text == t['action'][3]:
            find = True
        elif t['isElem']:
            idf1 = t['resource-id'] + ' ' + t['content-desc']
            idf2 = element.id + ' ' + element.desc
            find = idf1 == idf2
        if find:
            reverse_oracle = deepcopy(t)
            reverse_oracle['disappear'] = False
            reverse_oracle['activity'] = STL[idx].act
            STL[idx].oracle = reverse_oracle
            return idx
    if not find:
        if idx > 0:
            return trace_back(STL, t, idx - 1)
        else:
            return -1


def oracle_to_list(oracles, STL):
    tmp = []
    res = []
    for s_i in oracles:
        if (STL[s_i]).oracle.__contains__('disappear'):
            if not (STL[s_i].oracle)['disappear']:
                tmp.append(oracles[s_i])
        else:
            tmp.append(oracles[s_i])

    for e in tmp:
        id = e.id
        bounds = e.bounds
        cls = e.cls
        txt = e.text
        desc = e.desc
        r = {'id': id,
             'bounds': bounds,
             'cls': cls,
             'txt': txt,
             'desc': desc
             }
        res.append(r)
    return res


def res_to_list(res):
    tmp = []
    for e in res:
        id = e.id
        bounds = e.bounds
        cls = e.cls
        txt = e.text
        desc = e.desc
        r = {'id': id,
             'bounds': bounds,
             'cls': cls,
             'txt': txt,
             'desc': desc
             }
        tmp.append(r)
    return tmp


cate = '3'
type = '1'
folder = 'a' + cate + '_b' + cate + type
src = 'a' + cate + '5'
sdir = 'data/' + folder + '/tar/' + src + '/activitiesSummary.json'
test_json = 'data/' + folder + '/' + src + '.json'
sg = Parser_me.parseJson2STG(sdir)
file = open(test_json, "rb")
test = json.load(file)
stl = test_to_STL(test, sg)
print(stl)