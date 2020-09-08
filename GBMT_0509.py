# The main function
import copy
import math
import time

from Evaluation import evaluate
from Recorder import records
from Util_1 import init_elem_info, getPath, update_record
from simCal import *
from GlobleData import Gol


path_cache = [] # from prev_tgt to current_tgt
e_sim_cache = {}
haveMatched = []


def GBTM(): # SRC and TGT are arrays which record the activities
    # todo 1. add step cost and compare
    # todo 2. add input-display connection
    # todo 3.
    global SRC_G
    global TGT_G
    global T
    global G_SIM
    global step_limit
    SRC_G = Gol.get_value('SRC_G')  # graph info of source app
    TGT_G = Gol.get_value('TGT_G')  # graph info of target app
    T = Gol.get_value('T')  # the formatted original test file
    G_SIM = Gol.get_value('G_SIM')
    step_limit = Gol.get_value('step')
    match_record = {}
    prev_t = -1
    res = []
    path = []
    TGT_used = init_elem_info()
    for s_i in range(len(T)):
        print(s_i,'/',len(T))
        if prev_t != -1 and (s_i-1) in res:  #update the prev match_info
            match_i = res[s_i-1]
            if match_i != -1:
                updated_TGT_str = match_i['resource-id']+'_'+match_i['bounds']
                TGT_used[TGT_G[prev_t]].update({ updated_TGT_str: 1})
        step = 0
        sim, step_match_res, t_i, path_i = graph_match(s_i, prev_t, match_record, copy.deepcopy(TGT_used))
        if t_i != 'null':
            prev_t = t_i['activity']
            path.extend(path_i[0])
            res.append(t_i)
    records(res, path)





def graph_match(s_i: int, prev_t: str, match_record, TGT_used):
    max = -111
    matched_elem = 'null'
    record = []
    path = []
    if s_i >= len(T):
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


def sim_cal(s_i: int, t_i:str, prev_t:str, match_record:dict, TGT_used:dict):
    """ Calculate the sequence-similarity between [s_i:s_i+step] and [t_i:t_i+step]
    :param s_i: the index of handling action in source test file
    :param t_i: the id of considered target action
    :param prev_t: the id of previous matched graph (s_i-1<->prev_t.elem)
    :param match_record: records the matched info: {s_i:te_i,...s_n:te_n}
    :param TGT_used: records the matched elements in target, these elements shouldn't be matched twice
    :return: [total_sim: the similarity,
    matched_elem: the matched element of s_i,
    next_record: the following matched sequence]
    """
    graph_sim = graph_sim_cal(s_i, t_i, match_record, TGT_used)  # similar to tf-idf, + update graph
    edge_and_next_sim, matched_elem, record, result_path, jump_cost = path_sim_cal(s_i, t_i, prev_t, match_record, TGT_used)
    oracle_sim = oracle_sim_cal(s_i-1, t_i)
    total_sim = (graph_sim+edge_and_next_sim+oracle_sim)/jump_cost
    return total_sim, matched_elem, record, result_path


def graph_sim_cal(s_i, t_i, match_record, TGT_used):
    g_sim = 0
    updated = False
    if T[s_i].__contains__('chain'):
        s_input = T[s_i]['chain']
        t_match = match_record[s_i]
        if TGT_G[t_i].__contains__('chain'):
            if TGT_G[t_i]['chain'] == t_match:
                g_sim = 1
                updated = True
    if not updated:
        tgt_elems = get_unused_elem(t_i, TGT_used)
        src_elems = SRC_G[s_i]
        g_sim = graphSim_TFIDF(src_elems, tgt_elems)
    return g_sim



def oracle_sim_cal(prev_src, oracle):
    return 0


def path_sim_cal(s_i, t_i, prev_t, match_record, TGT_used):
    tmp, satisfy_paths = getPath(prev_t, t_i, path_cache)
    src_elem = T[s_i]
    sim = 0
    match_elem = 'null'
    next_record = []
    result_path = []
    tgt_step = 0
    #todo: what about the starting? in the starting point, sp = []
    jump_src = 0
    if s_i != 0:
        jump_src = 0 if T[s_i]['activity'] == T[s_i-1]['activity'] else 1
    jump_tgt = 0
    for sp in satisfy_paths: # sp = [evt1, evt2...]
        for i in range(len(sp)):
            decided_edge = sp[i]
            events = sp[i].target
            tgt_graph_id = sp[i].fromGraph
            for idx in range(len(events)):
                tar_elem = events[idx]  # tar_elem = [elem] or [elem1, elem2, ...]
                if isinstance(tar_elem, list):
                    for t_elem in tar_elem:
                        elem_score = elem_sim(t_elem, src_elem, TGT_used[tgt_graph_id], e_sim_cache)
                        new_TGT_used = update_record(t_elem, tgt_graph_id, TGT_used)
                        new_match_record = copy.deepcopy(match_record)
                        new_match_record.update({s_i:t_elem})
                        next_sim, next_record_tmp, m_elem, next_path = graph_match(s_i+1, t_i, new_match_record, new_TGT_used)
                        if elem_score + next_sim >= sim:
                            sim = elem_score + next_sim
                            match_graph = tgt_graph_id
                            match_elem = t_elem
                            match_elem["activity"] = tgt_graph_id
                            next_record = next_record_tmp
                            result_path.append(sp)
                            result_path.append(next_path)
                            jump_tgt = len(events)
                        #todo: add next_sim

                else:
                    elem_score = elem_sim(tar_elem, src_elem, TGT_used[tgt_graph_id], e_sim_cache)
                    new_TGT_used = update_record(tar_elem, tgt_graph_id, TGT_used)
                    new_match_record = copy.deepcopy(match_record)
                    new_match_record.update({s_i: tar_elem})
                    next_sim, next_record_tmp, m_elem, next_path = graph_match(s_i + 1, t_i, new_match_record,
                                                                               new_TGT_used)

                    if elem_score + next_sim >= sim:
                        sim = elem_score + next_sim
                        match_graph = tgt_graph_id
                        match_elem = tar_elem
                        match_elem["activity"] = tgt_graph_id
                        next_record = next_record_tmp
                        result_path.append(sp)
                        result_path.append(next_path)
                        jump_tgt = len(events)
                    # todo: add next_sim
    record = [match_elem]
    record.extend(next_record)
    jump_cost = 1 if s_i == 0 else math.log(abs(jump_tgt - jump_src) + 1, 2) + 1
    return sim, match_elem, record, result_path, jump_cost


def get_unused_elem(t_i, TGT_used):
    used_info = TGT_used[t_i]
    candidate = TGT_G[t_i]
    unused_elem = []
    for elem in candidate.elements:
        key = elem.id + '_' + elem.bounds
        if used_info[key] == 0:
            unused_elem.append(elem)
    return unused_elem


def elem_info_to_suffix(graph_info):
    suffix = ''
    for k in graph_info:
        suffix += graph_info[k]
    return suffix


def sim_edge_to_element(edge, src_elem, tgt_graph_id, prev_tgt_elem_info):
    # edge format:
    # 1. edge.elements = [evt1, evt2, evt3]  this means there are three edges between two graph
    # 2. edge.elements = [evt1, [evt2, evt3], evt4] this means there are three edges between two graph, where [evt2,evt3] must be triggered sequently
    evts = edge.target
    max = -1
    first = True
    match_tar_elem = -1
    for e in evts:
        if isinstance(e, list):  # e.g. ([evt1, evt2])
            for tar_elem in e:
                e_sim = elem_sim(tar_elem, src_elem, prev_tgt_elem_info[tgt_graph_id])
                if e_sim > max or first:
                    max = e_sim
                    match_tar_elem = tar_elem
                    first = False
        else:  # e.g. (evt1)
            tar_elem = e
            e_sim = elem_sim(tar_elem, src_elem, prev_tgt_elem_info[tgt_graph_id])
            if e_sim > max or first:
                max = e_sim
                first = False
                match_tar_elem = tar_elem
    return max, match_tar_elem


def updateMatched(matchEles, matchedSet):
    if isinstance(matchEles, list):
        matchEles = matchEles[len(matchEles) - 1]
    elif not isinstance(matchEles, dict) or matchEles == {}:
        return matchedSet

    ele = matchEles
    if isinstance(ele, list):
        ele = ele[len(ele) - 1]
    if not isinstance(ele, dict):
        return matchedSet
    eID = ele["resource-id"] if ele["resource-id"].find("/") == -1 else ele["resource-id"].split("/")[1]
    eText = ele["text"]
    eCls = ele["class"]
    eDesc = ele["content-desc"]
    eAct = ele["activity"]
    eKey = eID + "->" + eText + "->" + eCls + "->" + eDesc
    if eAct not in matchedSet:
        matchedSet[eAct] = []
    if eKey not in matchedSet[eAct]:
        matchedSet[eAct].append(eKey)
    return matchedSet


def sim_cal_edge_ver(tar_edge_list, src_elem, src_graph_idx, prev_tgt_elem_info, current_tgt_graph_id,
                     curr_sim, step_cost, e_match, last_match):
    """goal: removes the matched elements in prev_tar_graph, and returns the similar score elem_sim+graph_sim"""
    to_return_curr_sim = curr_sim
    to_return_e_match = e_match
    to_return_elem_info = prev_tgt_elem_info
    to_return_last_match = last_match
    tmp_last_match = {}
    last_sim = 0
    e_sim = 0
    match_elem = None
    match_graph = ''
    for i in range(len(tar_edge_list)):
        events = tar_edge_list[i].target
        tgt_graph_id = tar_edge_list[i].fromGraph
        for tar_elem in events:
            if isinstance(tar_elem, list):
                for t_elem in tar_elem:
                    elem_score = elem_sim(t_elem, src_elem, prev_tgt_elem_info[tgt_graph_id])
                    if elem_score >= e_sim:
                        e_sim = elem_score
                        match_graph = tgt_graph_id
                        match_elem = t_elem
                        match_elem["activity"] = tgt_graph_id

            else:
                elem_score = elem_sim(tar_elem, src_elem, prev_tgt_elem_info[tgt_graph_id])
                if elem_score >= e_sim:
                    e_sim = elem_score
                    match_graph = tgt_graph_id
                    match_elem = tar_elem
                    match_elem["activity"] = tgt_graph_id
    current_tgt_elem_info = copy.deepcopy(prev_tgt_elem_info)

    # if src_graph_idx == len(test_array)-1:
    #     last_sim, tmp_last_match = last_elem_handler(src_graph_idx, current_tgt_graph_id, current_tgt_elem_info)

    g_sim = graph_sim_cal(src_graph_idx, current_tgt_graph_id, current_tgt_elem_info)
    if match_elem is not None:
        if match_elem['type'] == "back":
            key = "back_none"
        else:
            key = str(match_elem['resource-id'] + '_' + match_elem['bounds'])
        current_tgt_elem_info[match_graph].update({key: 1})
    tmp_score = g_sim / step_cost + e_sim / step_cost + last_sim
    update = curr_sim < tmp_score
    if update:
        to_return_curr_sim = tmp_score
        if e_sim != 0:
            to_return_e_match = match_elem
        to_return_elem_info = current_tgt_elem_info
        to_return_last_match = tmp_last_match

    return to_return_curr_sim, to_return_e_match, to_return_elem_info, to_return_last_match
