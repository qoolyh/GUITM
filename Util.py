import copy
import json
import gensim
import numpy
from nltk.corpus import wordnet as wn
from itertools import product
import re
from GlobleData import Gol

model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit= 100000)


def elem_info_to_suffix(graph_info):
    suffix = ''
    for k in graph_info:
        suffix += graph_info[k]
    return suffix


def update_record(t_elem, graph_id, TGT_used):
    new_TGT_used = copy.deepcopy(TGT_used)
    if t_elem['type'] == "back":
        key = "back_none"
    else:
        key = str(t_elem['resource-id'] + '_' + t_elem['bounds'])
    new_TGT_used[graph_id].update({key: 1})
    return new_TGT_used


def init_elem_info():
    TGT_G = Gol.get_value('TGT_G')  # graph info of target app
    tar_elem_info = {}
    for id in TGT_G:
        tar_graph = TGT_G[id]
        elem_info = {}
        for e in tar_graph.elements:
            eid = e.id+'_'+e.bounds
            elem_info.update({eid: 0})
        tar_elem_info.update({id:elem_info})
    return tar_elem_info


def connected(idx1, idx2, am, visited):
    visited.append(idx1)
    connect = am[idx1][idx2] == 1 or idx1 == -1
    if connect:
        return True
    else:
        for i in range(len(am)):
            if am[idx1][i] == 1 and i not in visited:
                tmp = connected(i, idx2, am, visited)
                if tmp:
                    return True
    return connect


def get_edge(from_graph_id, to_graph_id):
    edge = []
    TGT_G = Gol.get_value('TGT_G')  # graph info of target app
    edges = TGT_G[from_graph_id].edges
    for e in edges:
        if e.toGraph == to_graph_id:
            edge = e
    return edge


def getPath(fromGraph, toGraph, visited):
    AM = Gol.get_value('adjencent_matrix')
    path_cache = Gol.get_value('path_cache')
    TGT_G = Gol.get_value('TGT_G')
    key = str(fromGraph)+'_'+str(toGraph)
    if path_cache.__contains__(key):
        return True, path_cache[key]
    else:
        if fromGraph == -1:
            return True, []
        visited.append(fromGraph)
        connect = AM.__contains__(key)
        way = []
        if connect:
            way.append([get_edge(fromGraph, toGraph)])
        for i in TGT_G:
            tmp_key = fromGraph+'_'+i
            if AM.__contains__(tmp_key) and i not in visited:
                tmp, ways = getPath(i, toGraph, visited)
                if tmp:
                    connect = tmp
                    for tmpPath in ways:
                        if tmpPath:
                            newPath = [get_edge(fromGraph, i)]
                            newPath.extend(tmpPath)
                            way.append(newPath)
    return connect, way


def readJson(filename):
    with open(filename) as f:
        content = json.load(f)
    return content


