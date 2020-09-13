import json
import os
from copy import deepcopy
from math import log
from tokenize import tokenize

from Parser_STL import oracle_to_list, res_to_list
from StrUtil import StrUtil
import simCal
from GlobleData import Gol
from SimUtil import elem_sim
from Util import getPath, find_out

delta = 2
state_cache = {}

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
    state_record = []
    oracle_record = {}
    prev_t = '-1'
    path = []
    per_evt = []
    s = 0
    for s_i in range(len(STL)):
        print(s_i, '/', len(STL))
        step = 0
        sim, state_i, path_i, oracle_i, per_evt_i = graph_match(s_i, prev_t, deepcopy(state_record), deepcopy(oracle_record), step)
        state_record.append(state_i[s_i])
        path.extend(path_i)
        if oracle_i:
            oracle_record.update({s_i: oracle_i})
        per_evt.extend(per_evt_i)
    print(state_i[len(state_i)-1], STL[len(STL)-1].act)
    records(path, per_evt, oracle_record)
    return s


def graph_match(s_i: int, prev_t: str, state_record: list, oracle_record: dict, step: int):
    """ find the best matching state t_i, s.t. 1) t_i is reachable from prev_t; 2) max(s[i,i+delta-step], t[i,i+delta-step])
    return the transition probability of two substring: s[i:i+delta-step], t[i, prev_t.reachable+delta-step]
    :param oracle_record:
    :param s_i:
    :param prev_t:
    :param state_record:
    :param step:
    :param sp:
    :return:
    """
    max = -111
    path = []
    state = state_record
    oracle = []
    per_evt = []
    if s_i >= len(STL) or step>delta:
        return 0, state, path, oracle, per_evt
    if prev_t == '-1':
        prev_t = Gol.get_value('tgt_start')
    counter = 1
    for t_i in TGT_G:
        # print(s_i,'considering....',counter,'/',len(TGT_G), step)
        counter+=1
        connect, paths = getPath(prev_t, t_i, [])
        sp = get_satisfy_paths(paths)
        if len(sp) > 0:
            state_record_i = deepcopy(state_record)
            state_record_i.append(t_i)
            sim_i, path_i, state_i, o_i, per_evt_i = sim_cal(s_i, t_i, state_record_i, oracle_record, step, sp)
            if max == -111 or sim_i > max:
                max = sim_i
                state = state_i
                path = path_i
                oracle = o_i
                per_evt = per_evt_i
    return max, state, path, oracle, per_evt


def sim_cal(s_i: int, t_i: str, state_record: list, oracle_record: dict, step: int, sp: list):
    """ Calculate the sequence-similarity between [s_i:s_i+step] and [t_i:t_i+step]

    :param state_record:
    :param s_i: the index of handling action in source test file
    :param t_i: the id of considered target action
    :param step: the step of current sublist matching
    :param oracle_record: records the matched oracles' info: {s_i.o:t_i.o,...}
    :param sp:
    :return: [total_sim: the similarity,
    best_path: the matched element of s_i,
    next_record: the following matched sequence]
    """
    if step == 2:
        a = 1
    oracle_record_i = deepcopy(oracle_record)
    if step > delta:
        return 0, [], [], []
    graph_sim = graph_sim_cal(s_i, t_i, state_record)  # similar to tf-idf, + update graph
    # graph_sim = 1
    edge_sim = 0
    path_i = []
    jump_cost = 1
    match_per_evt = []
    if s_i != 0:
        edge_sim, path_i, jump_cost, match_per_evt = path_sim_cal(s_i, sp)
    oracle_sim = 0
    o_match = []
    if hasattr(STL[s_i], 'oracle'):
        oracle_sim, o_match = oracle_sim_cal(STL[s_i].oracle, TGT_G[t_i], oracle_record_i)
        oracle_record_i.update({s_i: o_match})
    max = graph_sim + edge_sim + oracle_sim / jump_cost
    sim_next, states_next, path_next, oracles_next, _tmp = graph_match(s_i + 1, t_i, state_record, oracle_record_i, step + 1)
    max+= sim_next
    state_record = states_next
    #
    # path_k = []
    # record_k = []
    # state_k = []
    # for t_k in TGT_G:
    #     sim_k, states, path, oracles, _tmp = graph_match(s_i + 1, t_k, state_record, oracle_record_i, step + 1)
    #     if max + sim_k > max or max == -111:
    #         max = max + sim_k
    #         state_k = states
    #         path_k = path
    # state_record.extend(state_k)
    return max, path_i, state_record, o_match, match_per_evt


def get_satisfy_paths(paths):
    sp = []
    for p in paths:
        if len(p) <= delta:
            sp.append(p)
    return sp


def oracle_sim_cal(oracle, tgt_state, oracle_record):
    t_elems = tgt_state.elements
    if oracle.__contains__('disappear') and oracle['disappear']:
        bind = oracle['trace_back']
        match = oracle_record[bind]
        new_oracle = match
        if oracle['isTxt']:
            new_oracle.o_txt = match.text
            if not find_out(new_oracle.o_txt, tgt_state):
                return 1, new_oracle
            else:
                return 0, new_oracle
        else:
            new_oracle.o_id = match.id
            new_oracle.o_desc = match.desc
            new_oracle.disappear = True
            if not find_out(new_oracle, tgt_state):
                return 1, new_oracle
            else:
                return 0, new_oracle
    else:
        max = -111
        match = None
        for element in t_elems:
            # if oracle.__contains__('disappear'):
            #     if element.changable:
            #         sim = o_sim(oracle, element)
            #         if sim > max:
            #             max = sim
            #             match = element
            # else:
            sim = o_sim(oracle, element)
            if sim > max:
                max = sim
                match = element
    return max, match


def o_sim(oracle, element):
    sim = 0
    if isinstance(oracle, str):
        o_token = StrUtil.tokenize("text", oracle)
        e_token = StrUtil.tokenize("text", element.text)
        sim = simCal.arraySim(o_token, e_token)
    else:
        o_token = StrUtil.tokenize("content-desc", oracle['content-desc']) + (
            StrUtil.tokenize("resource-id", oracle['resource-id']))
        e_token = StrUtil.tokenize("content-desc", element.desc) + (StrUtil.tokenize("resource-id", element.id))
        sim = simCal.arraySim(o_token, e_token)
    return sim


def graph_sim_cal(s_i, t_i, match_record):
    g_sim = 0
    updated = False
    if hasattr(STL[s_i], 'IObind_from'):
        s_input = STL[s_i].IObind_from
        t_match = match_record[s_input]
        if hasattr(TGT_G[t_i], 'IObind_from'):
            if TGT_G[t_i].IObind_from == t_match:
                g_sim = 1
                updated = True
    if not updated:
        tgt_elems = TGT_G[t_i].elements
        src_elems = STL[s_i].elements
        g_sim = simCal.graphSim_TFIDF(src_elems, tgt_elems)
    return g_sim


def path_sim_cal(s_i: int, satisfy_paths: list):
    """
    Return the max similarity of P(path[i-1:i], path[prev_t:t_i])
    :param s_i:
    :param satisfy_paths:
    :return:
    """
    if s_i == 0:
        return 0, [], 1, []

    src_edge = STL[s_i - 1].edges
    match_elem = 'null'
    next_record = []
    decided_path = []
    match_per_evt = []
    max = -111
    jump_src = 0

    if s_i != 0:
        jump_src = 0 if STL[s_i - 1].act == STL[s_i] else 1
    jump_tgt = 0
    for sp in satisfy_paths:  # sp = [evt1, evt2...]
        if len(sp) <= delta:
            sp_tmp = deepcopy(sp)
            max_sp, match_info_sp = edge_comp(src_edge, sp_tmp)
            if max_sp > max or max == -111:
                max = max_sp
                match_per_evt = match_info_sp
                decided_path = sp
                jump_tgt = len(sp)

    record = [match_elem]
    record.extend(next_record)
    jump_cost = 1 if s_i == 0 else log(abs(jump_tgt - jump_src) + 1, 2) + 1
    # print(max, decided_path, jump_cost, match_per_evt)
    return max, decided_path, jump_cost, match_per_evt


def path_to_elem(path):
    res = []
    for edge in path:
        elems = edge.target
        for e in elems:
            if isinstance(e, list):
                for tmp in e:
                    res.append(tmp)
            else:
                res.append(e)
    return res


def e_sim_help(s_elems, t_elems, i, j, match):
    match_i = deepcopy(match)
    max = 0
    if i >= len(s_elems):
        return max, match_i
    if j >= len(t_elems):
        for l in range(i, len(s_elems)):
            match_i.append('null')
        return max, match_i
    for k in range(j, len(t_elems)):
        sim_k = elem_sim(s_elems[i], t_elems[k])
        match_k = deepcopy(match)
        match_k.append(t_elems[k])
        max_k, match_tmp = e_sim_help(s_elems, t_elems, i + 1, k + 1, match_k)
        total = sim_k + max_k
        if total > max:
            max = total
            match_i = match_tmp
    return max, match_i


def edge_comp(s_edge, path):
    s_elems = s_edge
    t_elems = path_to_elem(path)
    max_sim, match_info = e_sim_help(s_elems, t_elems, 0, 0, [])
    return max_sim, match_info


def records(path, per_evt, oracle):
    cate1 = Gol.get_value('cate1')
    cate2 = Gol.get_value('cate2')
    src = Gol.get_value('src')
    tgt = Gol.get_value('tgt')
    path_dir = 'result_UBTM/' + cate1 + '/' + cate2 + '/' + src + '_' + tgt + '_path.json'
    oracle_dir = 'result_UBTM/' + cate1 + '/' + cate2 + '/' + src + '_' + tgt + '_oracle.json'
    res_dir = 'result_UBTM/' + cate1 + '/' + cate2 + '/' + src + '_' + tgt + '_res.json'
    dir = 'result_UBTM/' + cate1 + '/' + cate2 + '/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(path_dir, 'w') as pf:
        json.dump(path_to_json(path), pf)
        pf.close()
    with open(oracle_dir, 'w') as of:
        res = oracle_to_list(oracle, STL)
        json.dump(res, of)
        of.close()
    with open(res_dir, 'w') as rf:
        # res = res_to_list(per_evt)
        # print(res)
        json.dump(per_evt, rf)
        rf.close()


def path_to_json(path):
    path_array = []
    for p in path:
        e_list = p.target
        for e in e_list:
            if isinstance(e, list):
                for e_i in e:
                    path_array.append(e_i)
            else:
                path_array.append(e)
    return path_array


def get_io_list(s_i):
    start = s_i
    end = s_i
    if hasattr(STL[s_i], 'IObind_to'):
        s_o = STL[s_i].IObind_to
        end = s_o
        for s_k in range(s_i+1, s_o):
            if hasattr(STL[s_k], 'IObind_to'):
                if STL[s_k].IObind_to > s_o:
                    end = STL[s_k].IObind
    return start, end
