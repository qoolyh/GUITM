import copy
import json

import numpy

import Parser_me as Parser
from GlobleData import Gol
from Parser_me import test_to_STL


def initAll(src_json, tar_json, test_json, sim_json, pair, tgt_start, cate, src, tgt):
        SRC_G = Parser.parseJson2STG(src_json)
        TGT_G = Parser.parseJson2STG(tar_json)
        file = open(test_json, "rb")
        test = json.load(file)
        STL = test_to_STL(test, SRC_G)
        file.close()
        T = Parser.parse_test_file(test_json)
        graph_sim_matrix = Parser.parse_graph_json(sim_json)[pair]
        step_limit = 3
        # src_elem_dicts_minus = initSrcDict(SRC_G, T)
        Gol.init()
        Gol.set_value('SRC_G', SRC_G)
        Gol.set_value('TGT_G', TGT_G)
        Gol.set_value('T', T)
        Gol.set_value('STL',STL)
        Gol.set_value('G_SIM', graph_sim_matrix)
        Gol.set_value('step', step_limit)
        Gol.set_value('path_cache', {})
        am = build_adjacency_matrix(TGT_G)
        Gol.set_value('adjencent_matrix', am)
        Gol.set_value('tgt_start', tgt_start)
        Gol.set_value('src',src)
        Gol.set_value('tgt',tgt)
        cates = cate.split('_')
        Gol.set_value('cate1',cates[0])
        Gol.set_value('cate2',cates[1])


def initSrcDict(SRC_G, T):
    # remove the triggered elements in the same activity
    src_elem_dicts_minus = []
    for i in range(len(T)):
        if "activity" not in T[i]:
            T[i]["activity"] = T[i - 1]["activity"]

    for i in range(len(T)):
        curr_idx = i
        prev_idx = i - 1
        if T[curr_idx]["class"] == "SYS_EVENT":
            elems = deleteElem(SRC_G[T[prev_idx]["activity"]].elements, T[prev_idx])
        elif T[curr_idx]["event_type"] != "oracle":
            elems = deleteElem(SRC_G[T[curr_idx]["activity"]].elements, T[curr_idx])
        src_elem_dicts_minus.append(elems)

    return src_elem_dicts_minus


def deleteElem(graph, elem):
    graph = copy.deepcopy(graph)
    elemId = elem["id"]
    for idx in range(len(graph)):
        eID = graph[idx].id if graph[idx].id.find("/") == -1 else graph[idx].id.split("/")[1]
        if eID == elemId:
            graph.pop(idx)
            break
    return graph


def build_adjacency_matrix(graphSet):
    am = {}
    for i in graphSet:
        edges = graphSet[i].edges
        for e in edges:
            toGraph = e.toGraph
            key = i+'_'+toGraph
            am.update({key:1})
    return am

