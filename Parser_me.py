import json
from copy import deepcopy

from Element import Element
from Edge import Edge
from Graph import Graph
import numpy
from Util import find_out


def parseJson2STG(jsonPath): # format: activity: graph_obj
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

        tmpG = Graph(gidx, elemArray, edgArray, actName)
        tmpG.act = actName
        graphs.update({actName: tmpG})
        gidx += 1
    return graphs


def oracle_parser(oracle_json):
    # action format: 0:action_type,
    # 1:time,
    # 2:action_subject (id, text, xpath),
    # 3:action_subject_detail (id_name, text_str)
    oracle = {}
    id = oracle_json['resource-id']
    if len(id)>0:
        sup_idx = id.index(':id/')
        if sup_idx>0:
            id = id[sup_idx+4:len(id)]
    action = oracle_json['action']
    oracle['activity'] = oracle_json['activity']
    oracle['expect'] = action[3]
    oracle['class'] = oracle_json['class']
    oracle['text'] = oracle_json['text']
    oracle['desc'] = oracle_json['content-desc']
    oracle['action'] = action
    oracle['id'] = id
    if len(id) == 0 and action[2] != 'xpath':  # which means the oracle expects to see a non-element
        oracle['is_elem'] = 0
    else:
        oracle['is_elem'] = 1
        e = Element(0, id, oracle_json['class'], oracle_json['text'], oracle_json['content-desc'], 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false')
        oracle['element'] = e
    oracle['target'] = id if len(id) != 0 else action[2]
    return oracle


def pass_to_prev(oracle_json, test_list, prev_idx):
    oracle = oracle_parser(oracle_json)
    test_list[prev_idx]['next'] = oracle
    test_list[prev_idx]['same'] = oracle['activity'] == test_list[prev_idx]['activity']


def getAM(graphSet):
    am = numpy.zeros((len(graphSet), len(graphSet)))
    for i in graphSet:
        edges = graphSet[i].edges
        for e in edges:
            toGraph = graphSet[e.toGraph].id
            am[graphSet[i].id][toGraph] = 1
    return am


def dict2array(dct): # format: idx:graphinfo
    array = []
    for k in dct:
        array.append(k)
    return array


# jp = r"D:\QQFile\MobileFile\send\src\a31\activitiesSummary.json"
# graphs = parseJson2STG(jp)
# keys = dict2array(graphs)
# for k in keys:
#     print(len(graphs[k].edges))


def parse_graph_json(json_dir):
    res = {}
    file = open(json_dir, "rb")
    sims = json.load(file)
    for pair in sims:
        sim_matrix = {}
        sup = pair.index('_')
        prev = pair[0:sup]
        next = pair[sup + 1:len(pair)]
        infos = sims[pair]
        for info in infos:
            act1 = info['act1']
            act2 = info['act2']
            act1 = act1[act1.index(prev) + len(prev) + 1:len(act1)]
            act1 = act1[0:act1.index('.xml')]
            act2 = act2[act2.index(next) + len(next) + 1:len(act2)]
            act2 = act2[0:act2.index('.xml')]
            if info['IDSim'] > 0.1 or info['TextSim'] > 0.1:
                new_info = {act1 + ' ' + act2: (info['IDSim'] + info['TextSim'] + info['ContentDescSim'])}
            else:
                new_info = {act1 + ' ' + act2: 0}
            sim_matrix.update(new_info)
        res.update({pair: sim_matrix})
    return res



# def parse_test_file(json_dir):
#     test_list = []
#     file = open(json_dir, "rb")
#     tests = json.load(file)
#     idx = 0
#     cursor = 0
#     for t in tests:
#         cursor += 1
#         mtype = t['event_type']
#         # if idx == 0 and mtype == 'oracle':
#         if mtype == 'oracle':
#             if idx > 0:
#                 pass_to_prev(t, test_list, idx - 1)
#             if cursor != len(tests):
#                 continue
#         if mtype == 'SYS_EVENT':
#             test_list.append(t)
#             idx += 1
#             continue
#         # if type != 'oracle':
#         id = t['resource-id']
#         sup = ':id/'
#         tmp = id
#         if len(id) > 0:
#             tmp = id[id.index(sup) + len(sup):len(id)]
#         id = tmp
#         t['id'] = id
#         text = t['text']
#         act = t['activity']
#         pwd = t['password']
#         clickable = t['clickable']
#         cls = t['class']
#         desc = t['content-desc']
#         e = Element(idx, id, cls, text, desc, 'false', 'false', clickable, 'false', 'false', 'false', pwd, mtype)
#         test_list.append(t)
#         idx += 1
#
#     return test_list


def parse_test_file(json_dir):
    test_list = []
    file = open(json_dir, "rb")
    tests = json.load(file)
    idx = 0
    for t in tests:
        type = t['event_type']
        if t.__contains__('resource-id'):
            t['id'] = t['resource-id']
        else:
            t['id'] = ''
        if type == 'oracle':
            if idx != 0:
                if test_list[idx-1]['class'] == 'SYS_EVENT':
                    if t['activity'] == test_list[idx-2]['activity']:
                        test_list[idx - 2]['oracle'] = t
                else:
                    if t['activity'] == test_list[idx-1]['activity']:
                        test_list[idx - 1]['oracle'] = t
            else:
                test_list.append(t)
                idx += 1
        elif type == 'SYS_EVENT':
            test_list.append(t)
            idx += 1
        else:
            test_list.append(t)
            idx += 1
    return test_list


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
            if len(STL) == 0:
                state.edges = [t]
                STL.append(state)
            else:
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