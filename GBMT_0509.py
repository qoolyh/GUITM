# The main function
import copy
import math
import time

from Evaluation import evaluate
from Recorder import records
from Util import init_elem_info, getPath, update_record
from simCal import *
from GlobleData import Gol


path_cache = [] # from prev_tgt to current_tgt
e_sim_cache = {}
haveMatched = []

#
# def GBTM(cate, src_folder, tgt_folder, suffix):
#
#     fileOBJ = open("data/" + cate + "/" + src_folder + "_" + tgt_folder + suffix + '.txt', 'w', encoding="utf-8")
#     start_time = time.time()
#     tarIndex = -1
#     res = {}
#     print("start " + src_folder + "_" + tgt_folder + "\n")
#     fileOBJ.write("start\n")
#     prev_elem_info = init_elem_info()
#     for i in range(len(T)):
#         if tarIndex != -1 and (i - 1) in res:
#             match_elem = res[i - 1]
#             if match_elem != -1:
#                 prev_elem_info[TGT_G[tarIndex]].update({match_elem['resource-id'] + '_' + match_elem['bounds']: 1})
#         score, tmpRes, ind = graph_match(i - 1, tarIndex, i, 0, copy.deepcopy(prev_elem_info))
#         tarIndex = ind
#         fileOBJ.write(str(tmpRes) + "\n")
#         fileOBJ.write(TGT_G[tarIndex] + "\n")
#         fileOBJ.write("--------------------------------------------------------" + "\n")
#         if i - 1 in tmpRes:
#             haveMatched[i - 1] = tmpRes[i - 1]
#             res[i - 1] = tmpRes[i - 1]
#     end_time = time.time()
#     record_time = str(end_time-start_time)


def GBTM(): # SRC and TGT are arrays which record the activities
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
    edge_and_next_sim, matched_elem, record, result_path = path_sim_cal(s_i, t_i, prev_t, match_record, TGT_used)
    oracle_sim = oracle_sim_cal(s_i-1, t_i)
    total_sim = graph_sim+edge_and_next_sim+oracle_sim
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
                    # todo: add next_sim
    record = [match_elem]
    record.extend(next_record)
    return sim, match_elem, record, result_path



def get_unused_elem(t_i, TGT_used):
    used_info = TGT_used[t_i]
    candidate = TGT_G[t_i]
    unused_elem = []
    for elem in candidate.elements:
        key = elem.id + '_' + elem.bounds
        if used_info[key] == 0:
            unused_elem.append(elem)
    return unused_elem
#
#
# def sim_cal_(s_i:int, t_i:int, prev_t, satisfy_paths: [], match_record:dict):
#     """
#     function that cals the similarity between s_i and t_i, returns the sum of g_sim, e_sim, and o_sim
#     :param s_i: handled source graph
#     :param t_i: handled target graph
#     :param prev_t: previous matched target graph, used for calculating the jumping cost of t_i
#     :param satisfy_paths: paths which length<=3 from prev_t to t_i
#     :param match_record:
#     :return:
#     """
#     t_elems = update_graph(t_i, match_record)
#     s_elems = SRC_G[s_i]
#     g_sim = graphSim_TFIDF(s_elems, t_elems)
#     next_match_record = {}
#     chosen_elem = -1
#     e_sim = 0
#     o_sim = 0
#     decided_elem = -1
#     next_sim_ordinary = -63
#     next_match_record_ordinary = {}
#     max_sim = 0
#     is_first = True
#     jump_s = 1 if SRC[s_i] != SRC[s_i - 1] else 0 # if the previous action locates in the same with current action, no jump
#     for path in satisfy_paths:
#         jump_t = len(path) if t_i != prev_t else 0 # will different paths have different jump costs?
#         jump_cost = math.log(abs(jump_s - jump_t) + 1, 2) + 1
#         for t_edge in path:
#             e_sim_tmp, e_match_tmp = edge_sim(t_edge, SRC_T[s_i]) # a list of elements considered, what about considering the last?
#             curr_sim_tmp = (g_sim + e_sim_tmp)/jump_cost
#             match_record_next = copy.deepcopy(match_record)
#             if is_input(SRC_T[s_i]):
#                 match_record_next.update({SRC_T[s_i]: e_match_tmp})
#                 next_sim, next_step_match_res, next_t = graph_match_v2(s_i+1, t_i, step+1, match_record_next, SRC, TGT)
#                 curr_sim_tmp += next_sim
#             else:
#                 if next_match_record_ordinary == -63:
#                     next_sim, next_step_match_res, next_t = graph_match_v2(s_i + 1, t_i, step + 1, match_record_next,
#                                                                            SRC, TGT)
#                     next_sim_ordinary = next_sim
#                     next_match_record_ordinary = next_step_match_res
#                     curr_sim_tmp += next_sim
#                 if is_first or max_sim < curr_sim_tmp:
#                     max_sim = curr_sim_tmp
#                     is_first = False
#                     decided_elem = e_match_tmp
#     return max_sim, decided_elem, next_match_record


def elem_info_to_suffix(graph_info):
    suffix = ''
    for k in graph_info:
        suffix += graph_info[k]
    return suffix


# def sim_cal(tar_edge, src_elem, src_graph_idx, tar_graph_id, step_cost, max_sim, e_match, prev_tgt_elem_info,
#             last_match):
#     to_return_elem_info = copy.deepcopy(prev_tgt_elem_info)
#     current_tgt_elem_info = copy.deepcopy(prev_tgt_elem_info)
#     to_return_e_match = e_match
#     to_return_max_sim = max_sim
#     to_return_last_match = last_match
#     e_sim, tar_match = sim_edge_to_element(tar_edge, src_elem, tar_graph_id, prev_tgt_elem_info)
#     graph_sim = graph_sim_cal(src_graph_idx, tar_graph_id, current_tgt_elem_info)
#     if tar_match != -1:
#         current_tgt_elem_info[tar_graph_id].update({tar_match['resource-id'] + '_' + tar_match['bounds']: 1})
#     tmp_score = graph_sim / step_cost + e_sim / step_cost
#     tmp_last_match = {}
#     # if src_graph_idx == len(test_array)-1:
#     #     last_sim, tmp_last_match = last_elem_handler(src_graph_idx, tar_graph_id, current_tgt_elem_info)
#     #     tmp_score += last_sim
#     update = max_sim < tmp_score
#     res = {}
#     if update:
#         to_return_elem_info = current_tgt_elem_info
#         to_return_max_sim = tmp_score
#         to_match = tar_match
#         to_return_last_match = tmp_last_match
#         if to_match != -1:
#             to_match["activity"] = tar_edge.fromGraph
#             to_return_e_match = to_match
#     return to_return_max_sim, to_return_e_match, to_return_elem_info, to_return_last_match


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


# def graph_update(src_id, tgt_id, match_info):
#     if src_bind.__contains__(src_id) and tgt_bind.__contains__(tgt_id):
#         if match_info.__contains__(src_id):
#             if tgt_bind[tgt_id][1] == match_info[src_id]:
#                 graph = tar_dict[tgt_id]
#                 for i in range(len(graph.elements)):
#                     e = graph.elements[i]
#                     if e.text == tgt_bind[tgt_id][1]['inputText']:
#                         tar_dict[tgt_id].elements[i].text = src_bind[src_id][1]['inputText']


# def graph_match(prev_tar_idx, curr_src_idx, steps, prev_tar_elem_info):
#     match = -1
#     match_graph_id = ''
#     score = 0
#     match_info = {}
#     resTarIndex = -1
#     pathStore = []
#     inner_last_match = {}
#     if steps == step_limit:
#         return score, {}, -1
#     if curr_src_idx == len(test_array):  # last not match
#         return score, {}, -1
#
#     # FOR BACK EVENT
#     if 'activity' in test_array[curr_src_idx]:
#         curr_src_graph = test_array[curr_src_idx]['activity']
#     else:
#         curr_src_graph = test_array[prev_src_idx]['activity']
#
#     # at the beginning
#     if prev_src_idx == -1:
#         current_tar_elem_info = prev_tar_elem_info
#         for i in range(len(tar_array)):
#             # if i <= 50:
#             #     continue
#             graph_sim = calculateGraphSim(curr_src_idx, tar_array[i])
#             if graph_sim == 0:
#                 continue
#             next_score, next_match, _ = graph_match(curr_src_idx, i, curr_src_idx + 1, steps + 1, current_tar_elem_info)
#             res = graph_sim + next_score
#
#             if res > score:
#                 score = res
#                 match_info = {prev_src_idx: None}
#                 match_info.update(next_match)
#                 resTarIndex = i
#         return score, match_info, resTarIndex
#
#     # at the internal
#     else:
#         e_match = -1
#         current_tgt_elem_info = prev_tar_elem_info
#         if 'activity' in test_array[prev_src_idx]:
#             prev_src_graph = test_array[prev_src_idx]['activity']
#         else:
#             prev_src_graph = test_array[prev_src_idx - 1]['activity']
#         step_src = 0 if similar(curr_src_graph, prev_src_graph) else 1
#         next_match_info = {}
#         key = 'com.contextlogic.wish.activity.login.signin.SignInActivity0'
#         if key not in prev_tar_elem_info:
#             a = 1
#             # print(a)
#         for i in range(len(tar_array)):
#             e_match = -1
#             # if i <= 2291 or i >= 40:
#             #     continue
#             curr_sim = 0
#             tar_graph_id = tar_array[i]
#             tar_graph = tar_dict[tar_graph_id]
#             src_elem = test_array[prev_src_idx]
#             # case 1, foraging from internal edges (point to itself)
#             if i == prev_tar_idx:
#                 matching_score = 0
#                 for tar_edge in tar_graph.edges:
#                     if tar_edge.toGraph == tar_edge.fromGraph:
#                         step_tar = 0
#                         step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
#                         curr_sim, e_match, current_tgt_elem_info, inner_last_match = sim_cal(tar_edge,
#                                                                                              src_elem,
#                                                                                              curr_src_idx,
#                                                                                              tar_graph_id,
#                                                                                              step_cost,
#                                                                                              curr_sim,
#                                                                                              e_match,
#                                                                                              prev_tar_elem_info,
#                                                                                              inner_last_match)
#             # case 2, foraging from external edges (point to other graphs)
#             else:
#                 connect, path = getPath(prev_tar_idx, i, adjacent_matrix_tar, [])
#                 if connect or i == prev_tar_idx:
#                     for p in path:  # a bug may arise if the event is in the middle of the path and the oracle matches t_i
#                         step_tar = len(p)
#                         if step_tar >= 3:
#                             continue
#                         step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
#                         curr_sim, e_match, current_tgt_elem_info, inner_last_match = sim_cal_edge_ver(p, src_elem,
#                                                                                                       curr_src_idx,
#                                                                                                       prev_tar_elem_info,
#                                                                                                       tar_graph_id,
#                                                                                                       curr_sim,
#                                                                                                       step_cost,
#                                                                                                       e_match,
#                                                                                                       inner_last_match)
#
#             if e_match == -1:
#                 continue
#             next_score, next_match, _ = graph_match(curr_src_idx, i, curr_src_idx + 1, steps + 1,
#                                                     copy.deepcopy(current_tgt_elem_info))
#             curr_sim += next_score
#             if score < curr_sim:
#                 score = curr_sim
#                 match = e_match
#                 next_match_info = next_match
#                 resTarIndex = i
#                 if prev_src_idx == 0:
#                     a = 1
#         match_info = {prev_src_idx: match}
#         match_info.update(next_match_info)
#
#         return score, match_info, resTarIndex


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
