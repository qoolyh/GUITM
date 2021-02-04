import copy
import json
import math
import re

from numpy.core.defchararray import isnumeric

import Init
import Util
from StrUtil import StrUtil
import simCal
from InputGenerator import get_input, getAnswer
from Parser_STL import test_to_STL
from Parser_me import parseJson2STG
from simCal import single_elem_sim

ANS = {}


def exhaustive_search(SRC_ipts, TGT_ipts, ans, SRC, TGT):
    res = {}
    map = sort_by_graph_sim(SRC_ipts, TGT_ipts, SRC, TGT, ans)
    for i in SRC_ipts:
        look_forward = 0
        ipt = SRC_ipts[i]
        tgts = map[i]
        for tgt in tgts:
            use_next = 0
            if tgt not in ans:
                continue
            sorted_ipt = priority_rank_A(ipt['ipts'], TGT_ipts[tgt])
            for comp in sorted_ipt:
                if check(comp, ans[tgt]):
                    if tgt not in res:
                        res.update({tgt: comp})
                        look_forward += 1
                    if look_forward > 3:
                        break  # once you break, no more tgts will be matched
    return res


def sort_by_graph_sim(SRC_ipts, TGT_ipts, SRC, TGT, ans):
    # return gsim({si: [tj, tj+1]}, {si+1: [tk,tk+1]}...)
    gsim_Ranked = {}
    counter = 1
    for s in SRC_ipts:
        si = {}
        score = []
        tmp = []
        tcounter = 1
        for t in TGT_ipts:
            if t not in ans:
                tcounter += 1
                continue
            src_i = SRC[s]
            tgt_i = TGT[t]
            gsim_i = simCal.gSim_baseline(src_i.elements, tgt_i.elements)
            if si.__contains__(gsim_i):
                si[gsim_i].append(t)
            else:
                si.update({gsim_i: [t]})
                score.append(gsim_i)
            tcounter += 1
        score.sort(reverse=True)
        for k in score:
            tmp.extend(si[k])
        gsim_Ranked.update({s: tmp})
        counter += 1
    return gsim_Ranked


def getInputEdges(STG):
    iptEdge = {}
    for s in STG:
        state = STG[s]
        key = s
        path = state.edges
        egs = []
        for edges in path:
            tmp = []
            elements = edges.target
            if len(elements) > 1:
                for e in elements:
                    if isinstance(e, list):
                        tmp_e = []
                        for k in e:
                            if k['type'] == 'input':
                                tmp_e.append(k)
                        if len(tmp_e) > 1:
                            egs.append(tmp_e)
                    else:
                        if e['type'] == 'input':
                            tmp.append(e)
            if len(tmp) > 0:
                egs.append(tmp)
        if len(egs) > 0:
            iptEdge.update({key: egs})
    return iptEdge


def get_input_from_STG(STG):
    ipts = {}
    for s in STG:
        iptElem = []
        state = STG[s]
        key = s
        path = state.edges
        egs = []
        for edges in path:
            elements = edges.target
            if len(elements) > 1:
                for e in elements:
                    if isinstance(e, list):
                        tmp_e = []
                        for k in e:
                            if k['type'] == 'input':
                                if k not in iptElem:
                                    iptElem.append(k)
                    else:
                        if e['type'] == 'input':
                            if e not in iptElem:
                                iptElem.append(e)
        if len(iptElem) > 0:
            ipts.update({key: iptElem})
    return ipts


def check(ipt_comb, ans):
    correct = True
    key = ''
    ipt_words = []
    for i in range(len(ipt_comb)):
        if '.net' in ipt_comb[i]['action'][1]:
            if '.net' in ans[i]:
                continue
            else:
                correct = False
                break
        if ipt_comb[i]['action'][1] == ans[i] or ans[i] == '666':
            continue
        else:
            correct = False
            break
    return correct


def priority_rank_A(ipts, edge):
    comp = []
    if len(edge) == 0:
        return comp
    ranked_ipt = rank(ipts, edge[0])
    for i in range(len(ranked_ipt)):
        copy_ipt = copy.deepcopy(ranked_ipt)
        copy_ipt.pop(i)
        copy_edge = copy.deepcopy(edge)
        copy_edge.pop(0)
        left = priority_rank_A(copy_ipt, copy_edge)
        if len(left) == 0:
            comp.append([ranked_ipt[i]])
        else:
            for k in left:
                new_comp_k = [ranked_ipt[i]]
                new_comp_k.extend(k)
                comp.append(new_comp_k)
    return comp


def rank(ipts, target):
    ranked_ipt = []
    score2ipt = {}
    scores = []
    for i in ipts:
        score = single_elem_sim(i, target)
        if score2ipt.__contains__(score):
            score2ipt[score].append(i)
        else:
            score2ipt.update({score: [i]})
            scores.append(score)
    scores.sort(reverse=True)
    for s in scores:
        ranked_ipt.extend(score2ipt[s])
    return ranked_ipt


def main():
    global STG
    global STL
    cate = '3'
    type = '1'
    folder = 'a' + cate + '_b' + cate + type
    src = 'a' + cate + '5'
    ref = 'a' + cate + '2'

    sdir = 'data/' + folder + '/tar/' + src + '/activitiesSummary.json'
    tdir = 'data/' + folder + '/tar/' + ref + '/activitiesSummary.json'
    test_json = 'data/' + folder + '/' + src + '.json'
    ansjson = 'data/' + folder + '/' + ref + '.json'

    start_tgt = 'com.contextlogic.wish.activity.login.createaccount.CreateAccountActivity0'
    # start_tgt = 'com.yelp.android.nearby.ui.ActivityNearby0'
    sim_json = "data/a3_b31/sim_a35.json"
    Init.initAll(sdir, tdir, test_json, sim_json, "a35_a31", start_tgt, 'a3_b31', src, ref)

    sg = parseJson2STG(sdir)
    tg = parseJson2STG(tdir)
    file = open(test_json, "rb")
    test = json.load(file)

    file2 = open(ansjson, "rb")
    ansf = json.load(file2)
    STL = test_to_STL(test, sg)
    STG = tg
    oracle_binding(STL)
    tipt = get_input_from_STG(tg)
    sipt = get_input(STL)
    for tmp in tipt:
        find_binds(tmp, tg, tipt)
    ans = getAnswer(ansf)
    res = exhaustive_search(sipt, tipt, ans, sg, tg)

    visited = []
    tgt_paths = []
    SI_paths, IO_paths = STG_pruning(tg, res, start_tgt)
    SI_path_src, IO_path_src = divide_STL(STL, res)
    test_path(IO_path_src, IO_paths, SI_paths, SI_path_src[-1].edges[-1])
    # for p in IO_paths:
    #     io_pairs = IO_paths[p]
    #     print('_____________', p)
    #     i = 1
    #     for desitination_paths in io_pairs:
    #         print('path____', i)
    #         i += 1
    #         for destination in desitination_paths:
    #             v = simCal.o_sim(STL[-1], tg[destination])
    #             print(v)
    # paths = desitination_paths[destination]
    # for path in paths:
    #     print('one path')
    #     for edge in path:
    #        print(edge.fromGraph, edge.toGraph, edge.target)

    # for r in res:
    #     tgt_ipt = r
    #     src_ipts = res[r]
    #     print(tgt_ipt, src_ipts)
    #     paths_r = Util.getPath(start_tgt, r, visited)
    #     print('from ',start_tgt, ' to', r)
    #     if hasattr(tg[r], 'binding'):
    #         r_binding = tg[r].binding
    #         for k in r_binding:
    #             paths_2 = Util.getPath(r, k, [])
    #             print('__from ', r, ' to', k)
    #             for pr in paths_2[1]:
    #                 for e in pr:
    #                     print(e.fromGraph, e.toGraph)
    #                 print('____________')


def STG_pruning(STG, ipt_matching_res, start_tgt):
    SI_paths = []  # getting paths from start to correct_inputting states
    IO_paths_list = []
    IO_paths = {}
    for r in ipt_matching_res:
        tgt_ipt = r
        src_ipts = ipt_matching_res[r]
        connect, si_paths_r = Util.getPath(start_tgt, r, [])
        SI_paths.extend(si_paths_r)
        # SI_paths.update({r: si_paths_r[1]})
        if hasattr(STG[r], 'binding'):
            r_bindings = STG[r].binding  # one input may bind to multiple displays
            for k in r_bindings:
                io_paths_k = Util.getPath(r, k, [])
                if IO_paths.__contains__(r):
                    IO_paths[r].append(io_paths_k[1])
                else:
                    IO_paths.update({r: [io_paths_k[1]]})
    for k in IO_paths:
        IO_k = IO_paths[k]
        for act in IO_k:
            IO_paths_list.extend(act)
    return SI_paths, IO_paths_list


def idxof(STL, act):
    counter = 0
    find = False
    for k in STL:
        if k.act == act:
            find = True
            break
        counter += 1
    if find:
        return counter
    else:
        return -1


def divide_STL(STL, res):
    SI_paths = {}
    IO_paths = {}
    ipt_states = []
    for k in res:
        ipts = res[k]
        for i in ipts:
            if i['activity'] not in ipt_states:
                ipt_states.append(i['activity'])
    idx = idxof(STL, ipt_states[-1])
    if idx != -1:
        SI_paths = STL[0:idx + 1]
        IO_paths = STL[idx: len(STL)]
    return SI_paths, IO_paths


def matching(src_path, tgt_paths, SI=False):
    for tgt_path in tgt_paths:
        path_match(src_path, tgt_path, SI, )


def test_path(path_src, paths_tgt, SI_paths, prev_src_e):
    prev_tgt_evts = []
    forSI = False
    prev_tgt = -1

    for path_tgt in paths_tgt:
        start = path_tgt[0].fromGraph
        for sip in SI_paths:
            if sip[-1].toGraph == start:
                prev_tgt_evts = sip[-1]
                score, path, events = path_match(path_src, path_tgt, forSI, -1, prev_tgt, True, prev_src_e,
                                                 prev_tgt_evts)
                print(score)
                for e in path:
                    print(e.fromGraph, e.toGraph, e.target)
                print('evts', events)


def path_match(path_src, path_tgt, forSI, prev_src, prev_tgt, begining, prev_src_e=[], prev_events_tgt=[]):
    max = 0
    path = []
    events = []
    prev_evt_src = ''
    if len(path_src) == prev_src + 1:
        return max, path, events
    if len(path_tgt) == prev_tgt + 1:
        for i in range(len(path_src)):
            events.append('none')
        return max, path, events
    if not begining:
        prev_evt_src = path_src[prev_src].edges[-1]
    if not forSI and begining:
        prev_evt_src = prev_src_e
    # if prev_src == len(path_src)-2 or prev_tgt == len(path_tgt)-2:
    #     jump_src = len(path_src) - prev_src -1
    #     jump_tgt = len(path_tgt) - prev_tgt -1
    #     max = math.log(abs(jump_tgt - jump_src) + 1, 2) + 1

    for idx in range(prev_tgt + 1, len(path_tgt)):
        first_t = ''
        edge = path_tgt[idx]
        if isinstance(edge, list):
            first_t = edge[-1].fromGraph
        else:
            first_t = edge.fromGraph
        event_sim = 0
        matched_path = []
        matched_event = []
        if not begining:
            prefixes = path_tgt[prev_tgt:idx]
            print(prev_evt_src)
            event_sim, matched_path, matched_event = find_best_event(prefixes, prev_evt_src)
        elif not forSI:
            if idx == 0:  # IO beginning
                seq_sim, matched_seq, matched_events = path_match(path_src, path_tgt, forSI, prev_src + 1, idx, False)
                sim_t = seq_sim
                path_t = matched_seq
                events_t = matched_events
                return sim_t, path_t, events_t
            else:
                break
        graph_sim = simCal.gSim_baseline(STL[0].elements, STG[first_t].elements)
        oracle_sim, matched_oracle = simCal.o_sim(STL[0], STG[first_t])
        if matched_oracle == '':
            oracle_sim = 0
        seq_sim, matched_seq, matched_events = path_match(path_src, path_tgt, forSI, prev_src + 1, idx, False)
        sim_t = event_sim + graph_sim + oracle_sim + seq_sim
        path_t = copy.deepcopy(matched_path)
        path_t.extend(matched_seq)
        events_t = copy.deepcopy(matched_event)
        events_t.extend(matched_events)
        if sim_t > max:
            max = sim_t
            path = path_t
            events = events_t
    return max, path, events
    # else:
    #     max = 0
    #     path = {}
    #     prev_evt_src = STL[prev_src].edges[-1]
    #     for first_t in path_tgt:
    #         connect, prefixes = Util.getPath(prev_tgt, path_tgt[first_t], [], True)
    #         event_sim, matched_path, matched_event = find_best_event(prefixes, prev_evt_src)
    #         graph_sim = simCal.gSim_baseline(STL[0], STG[first_t])
    #         oracle_sim = simCal.o_sim(STL[0], STG[first_t])
    #         seq_tgt = subSeq(path_tgt, first_t)
    #         seq_src = subSeq(path_src, list(path_src)[0])
    #         seq_sim, matched_seq, matched_events = path_match(seq_src, seq_tgt, forSI, list(path_src)[0], first_t, STL, STG)
    #
    #         seq_sim, matched_seq, matched_events = seq_matcher(path_src, seq_tgt)


def pmatch(path_src, path_tgt, forSI, prev_src, prev_tgt, begining, prev_src_e=[], prev_events_tgt=[]):
    max = 0
    path = []
    events = []
    prev_evt_src = ''
    if len(path_src) == prev_src + 1:
        return max, path, events
    if len(path_tgt) == prev_tgt + 1:
        for i in range(len(path_src)):
            events.append('none')
        return max, path, events
    for k in range(prev_src + 1, len(path_src)):
        for l in range(prev_tgt, len(path_tgt)):
            sim_kl, path_kl, events_kl = sim(path_src[prev_src, k], path_tgt[prev_tgt, l], begining)
            nextSim, path_next, events_next = pmatch(path_src, path_tgt, forSI, k, l, False)
            if sim_kl + next > max:
                max = sim_kl + next
                path = path_kl
                events = events_kl
                path.extend(path_next)
                events.extend(events_next)
    return max, path, events


def sim(subp_src, subp_tgt, beginning):
    max = 0
    path = []
    events = []

    evt_src = to_events(subp_src, True)
    evt_tgt = to_events(subp_tgt)
    score, record = basicDP(evt_src, evt_tgt, -1, -1, single_elem_sim)
    if beginning:
        a = 1
    return max, path, events


def to_events(path, forSrc=False):
    evts = []
    for g in path:
        if forSrc:
            evts.append(g.edges[-1])
        else:
            target = g.target
            if isinstance(target, list):
                target = target[-1]
            if isinstance(target, list):
                target = target[-1]
            evts.append(target)
    return evts


DP_res = {}


def basicDP(list1, list2, start1, start2, func, init=False):
    if init:
        DP_res.clear()
    max = 0
    record = []
    i = start1 + 1
    rec_i = []
    score_i = 0
    match_i = -1
    if i <len(list1):
        for j in range(start2 + 1, len(list2)):
            key = str(i)+'_'+str(j)
            if key in DP_res:
                max_i, record_i = DP_res[key]
                if max< max_i:
                    max = max_i
                    record = record_i
                continue
            v = func(list1[i], list2[j])
            left, left_rec = basicDP(list1, list2, i, j, func)
            left_ban, left_rec_ban = basicDP(list1, list2, i, start2, func)
            left_kpt, left_rec_kpt = basicDP(list1, list2, start1, j, func)
            if max <= v+left:
                max = v+left
                record = [j]+left_rec
            if max <= left_kpt:
                max = left_kpt
                record = left_rec_kpt
            if max <= left_ban:
                max = left_ban
                record = [-1]+left_rec_ban
            DP_res.update({key:[max, record]})
    return max, record


def find_best_event(path, src_evt):
    best_path = []
    matched_event = []
    max_score = -1
    if isinstance(path, list):
        for edge in path:
            jump = len(path)
            jump_cost = math.log(abs(jump - 1) + 1, 2) + 1
            event = edge.target
            if isinstance(event, list):
                event = event[-1]
            if isinstance(event, list):
                event = event[-1]
            esim_curr = simCal.single_elem_sim(src_evt, event) / jump_cost
            if esim_curr > max_score:
                max_score = esim_curr
                matched_event = [event]
                best_path = path
    else:
        edge = path
        jump = 1
        jump_cost = math.log(abs(jump - 1) + 1, 2) + 1
        event = edge.target
        if isinstance(event, list):
            event = event[-1]
        esim_curr = simCal.single_elem_sim(src_evt, event) / jump_cost
        if esim_curr > max_score:
            max_score = esim_curr
            matched_event = [event]
            best_path = [path]
    return max_score, best_path, matched_event


def subSeq(seq, start):
    res = {}
    find = False
    for key in seq:
        if key == start:
            find = True
            if find:
                res.update({key: seq[key]})
    return res


def oracle_binding(STL):
    oracles = []
    for s in STL:
        if hasattr(s, 'oracle'):
            oracles.append(s.oracle)
    STL_ipts = get_input(STL)
    for o in oracles:
        o_text = o['text']
        o_desc = o['content-desc']
        o_content = o_text + ' ' + o_desc
        for act in STL_ipts:
            ipts = STL_ipts[act]['ipts']
            idx = STL_ipts[act]['idx']
            for i in ipts:
                flag = False
                if isNum(o_text) and isNum(i['action'][1]):
                    flag = True
                text = i['text'] + ' ' + i['action'][1]
                if similar_substr(text, o_content):
                    flag = True
                if flag:
                    if not hasattr(STL[idx], 'binding'):
                        STL[idx].binding = {}
                    if 'activity' in o:
                        if STL[idx].binding.__contains__(o['activity']):
                            STL[idx].binding[o['activity']].append(i['resource-id'])
                        else:
                            STL[idx].binding = {o['activity']: [i['resource-id']]}


def find_binds(sid, STG, ipts):
    lamda = 3
    accessble_states = dfs(STG[sid], STG, lamda)
    for accs in accessble_states:
        txts = ipts[sid]
        for t in txts:
            res = contain_str(t['inputText'], STG[accs])
            if len(res) > 0:
                for e in res:
                    if not hasattr(STG[sid], 'binding'):
                        STG[sid].binding = {}
                    if STG[sid].binding.__contains__(accs):
                        if t['resource-id'] not in STG[sid].binding[accs]:
                            STG[sid].binding[accs].append(t['resource-id'])
                    else:
                        STG[sid].binding.update({accs: [t['resource-id']]})


def contain_str(st, state):
    res = []
    elems = state.elements
    for e in elems:
        if isNum(st):
            if isNum(e.text):
                res.append(e)
        if similar_substr(st, e.text):
            res.append(e)
    return res


def dfs(ipt_state, STG, lamda):
    res = []
    if lamda == 0:
        return []
    else:
        for edge in ipt_state.edges:
            toGraph = edge.toGraph
            res.append(toGraph)
            tmp = dfs(STG[toGraph], STG, lamda - 1)
            if tmp:
                res.extend(tmp)
    return res


def similar_substr(text, o_content):
    tk1 = StrUtil.tokenize('text', text)
    tk2 = StrUtil.tokenize('text', o_content)
    same = False
    for t1 in tk1:
        for t2 in tk2:
            if t1 == t2:
                return True
    return same


def isNum(s):
    if isnumeric(s):
        return True
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False


def moreThanOneIpt(STL):
    ipt = get_input(STL)
    counter = 0
    prev = ''
    for i in ipt:
        print(i)
        if prev:
            if i == prev:
                continue
            else:
                print(prev, i)
                prev = i
        else:
            prev = i

# main()

# for si in sg:
#     if 'CreateAccountActivity' in si:
#         for ti in tg:
#             v = simCal.gSim_baseline(sg[si].elements, tg[ti].elements)
#             print(si, ti)
#             print(v)
#         break


# ipt_p = 'data/a3_b31/a31.json'
# tgt_p = 'data/a3_b31/a32.json'
# # ans = getAnswer(tgt_p)
# ipt_file = open(ipt_p, "rb")
# ipts = json.load(ipt_file)
# ipt_file.close()
# tgt_file = open(tgt_p, "rb")
# tgts = json.load(tgt_file)
# tgt_file.close()
# STG = parseJson2STG('data/a3_b31/tar/a32/activitiesSummary.json')
#
# ipt = []
# tgt = []
# egs = getInputEdges(STG)
# for eg in egs:
#     print(egs[eg])


# for i in ipts:
#     if 'send_keys' in i['action'][0]:
#         ipt.append(i)
# for i in tgts:
#     if 'send_keys' in i['action'][0]:
#         tgt.append(i)
#
# res = priority_rank_A(ipt, [tgt[1]])
# for r in res:
#     print(r)
# print(res)
