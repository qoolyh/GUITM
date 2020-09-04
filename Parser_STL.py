import json
from copy import deepcopy

from Edge import Edge
from Element import Element
from Graph import Graph


def json_to_STG(jsonPath): # format: activity: graph_obj
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
    oracle = []
    idx = 0
    for t in test:
        t['idx'] = idx
        idx+=1
        last = len(STL)-1
        if t['event_type'] == 'gui':
            t['isInput'] = 'send_keys' in t['action']
            act = t['activity']
            state = deepcopy(SRC[act])
            if oracle:
                o_act = oracle['activity']
                if o_act == act:
                    state.oracle = oracle
                    oracle = []
            if not STL:
                state.edges = [t]
                STL.append(state)
            else:
                if act == STL[last].act:
                    STL[last].edges.append(t)
                else:
                    state.edges = [t]
                    STL.append(state)
        elif t['event_type'] == 'SYS_EVENT':
            act = STL[last-1].act
            state = deepcopy(SRC[act])
            state.edges = [t]
            STL.append(state)
        else:
            if not STL:
                continue
            if t.__contains__('activity'):
                t['isElem'] = 'element' in t['action'][0]
                t['isTxt'] = 'text' in t['action'][0]
                t['oTxt'] = t['action'][3] if t['isTxt'] else ''
                t['disappear'] = 'invisible' in t['action'][0]
                act = t['activity']
                if act == STL[last].act:
                    STL[last].oracle = t
                else:
                    oracle = t
                    if idx == len(test):
                        state = deepcopy(SRC[act])
                        state.oracle = oracle
                        state.edges = []
                        STL.append(state)
            else:
                STL[last].oracle = t

    return STL



