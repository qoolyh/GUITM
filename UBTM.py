from copy import deepcopy
from math import log

import simCal
from GlobleData import Gol
from SimUtil import elem_sim
from Util import getPath

delta = 3

def UBTM():
    global SRC_G
    global TGT_G
    global STL
    global G_SIM
    global step_limit
    SRC_G = Gol.get_value('SRC_G')  # graph info of source app
    TGT_G = Gol.get_value('TGT_G')  # graph info of target app
    STL = Gol.get_value('STL')  # the formatted original test file
    G_SIM = Gol.get_value('G_SIM')
    step_limit = Gol.get_value('step')
    match_record = {}
    prev_t = -1
    res = []
    path = []
    TGT_used = init_elem_info()
    for s_i in range(len(STL)):
        print(s_i, '/', len(STL))
        if prev_t != -1 and (s_i - 1) in res:  # update the prev match_info
            match_i = res[s_i - 1]
            if match_i != -1:
                updated_TGT_str = match_i['resource-id'] + '_' + match_i['bounds']
                TGT_used[TGT_G[prev_t]].update({updated_TGT_str: 1})
        step = 0
        sim, step_match_res, t_i, path_i = graph_match(s_i, prev_t, match_record, deepcopy(TGT_used), delta)
        if t_i != 'null':
            prev_t = t_i['activity']
            path.extend(path_i[0])
            res.append(t_i)
    records(res, path)


def graph_match(s_i: int, prev_t: str, match_record, TGT_used, delta):
    max = -111
    matched_elem = 'null'
    record = []
    path = []
    if s_i >= len(STL):
        return max, record, matched_elem, path
    if prev_t == -1:
        prev_t = Gol.get_value('tgt_start')
    for t_i in TGT_G:
        sim_i, matched_i, record_i, path_i = sim_cal(s_i, t_i, prev_t, match_record, TGT_used)
        if max == -111 or sim_i > max:
            max = sim_i
            matched_elem = matched_i
            path = path_i
            record = record_i
    return max, record, matched_elem, path


def sim_cal(s_i: int, t_i:str, prev_t:str, match_record:dict, step):
    """ Calculate the sequence-similarity between [s_i:s_i+step] and [t_i:t_i+step]
    :param s_i: the index of handling action in source test file
    :param t_i: the id of considered target action
    :param prev_t: the id of previous matched graph (s_i-1<->prev_t.elem)
    :param match_record: records the matched info: {s_i:te_i,...s_n:te_n}
    :return: [total_sim: the similarity,
    matched_elem: the matched element of s_i,
    next_record: the following matched sequence]
    """
    graph_sim = graph_sim_cal(s_i, t_i, match_record)  # similar to tf-idf, + update graph
    edge_sim, path, jump_cost = path_sim_cal(s_i, t_i, prev_t, match_record)
    oracle_sim = oracle_sim_cal(s_i, t_i)
    curr_sim = graph_sim + edge_sim + oracle_sim / jump_cost
    match_record_i = deepcopy(match_record)
    match_record_i.append(t_i)
    for t_k in TGT:
        if reachable(t_i, t_k, delta, path_cache, distance):
            sim_k, record_k, path_k = sim_cal(s_i+1, t_k, match_record_i)


    total_sim = (graph_sim+edge_sim+oracle_sim)/jump_cost
    return total_sim, matched_elem, record, result_path


def graph_sim_cal(s_i, t_i, match_record, TGT_used):
    g_sim = 0
    updated = False
    if STL[s_i].__contains__('chain'):
        s_input = STL[s_i]['chain']
        t_match = match_record[s_i]
        if TGT_G[t_i].__contains__('chain'):
            if TGT_G[t_i]['chain'] == t_match:
                g_sim = 1
                updated = True
    if not updated:
        tgt_elems = get_unused_elem(t_i, TGT_used)
        src_elems = STL[s_i].elements
        g_sim = simCal.graphSim_TFIDF(src_elems, tgt_elems)
    return g_sim


def path_sim_cal(s_i, t_i, prev_t, match_record, TGT_used):
    tmp, satisfy_paths = getPath(prev_t, t_i, path_cache)
    src_edge = STL[s_i-1].edges
    sim = 0
    match_elem = 'null'
    next_record = []
    result_path = []
    tgt_step = 0
    max = -111
    #todo: what about the starting? in the starting point, sp = []
    jump_src = 0
    if s_i != 0:
        jump_src = 0 if STL[s_i-1].act == STL[s_i] else 1
    jump_tgt = 0
    for sp in satisfy_paths: # sp = [evt1, evt2...]
        max_sp, match_info_sp = edge_comp(src_edge, sp)
        if max_sp > max or max == -111:
            max = max_sp
            match_record = match_info_sp
            result_path = sp
            jump_tgt = len(sp)

    record = [match_elem]
    record.extend(next_record)
    jump_cost = 1 if s_i == 0 else log(abs(jump_tgt - jump_src) + 1, 2) + 1
    return sim, result_path, jump_cost


def path_to_elem(path):
    res = []
    for edge in path:
        elems = edge.target
        for e in elems:
            res.append(e)
    return res


def e_sim_help(s_elems, t_elems, i, j):
    max = 0
    match = []
    if i >= len(s_elems):
        return max, match
    if j >= len(t_elems):
        for l in range(i,len(s_elems)):
            match[s_elems[l]['idx']] = 'null'
        return max, match
    for k in range(j,len(t_elems)):
        sim = elem_sim(s_elems[i], t_elems[k])
        max_k, match_k = e_sim_help(s_elems, t_elems, i+1, k+1)
        total = sim + max_k
        if total > max:
            max = total
            match[s_elems[i]['idx']] = t_elems[k]
            match.extend(match_k)
    return max, match


def edge_comp(s_edge, path):
    s_elems = s_edge
    t_elems = path_to_elem(path)
    max_sim, match_info = e_sim_help(s_elems, t_elems, 0, 0)
    return max_sim, match_info