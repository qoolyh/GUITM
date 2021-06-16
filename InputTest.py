import copy
import json
import math
import re
from collections import OrderedDict

import numpy
from numpy.core.defchararray import isnumeric

from Edge import Edge
import Init
from SeqMatcher import SeqMatcher
import Util
from StrUtil import StrUtil
import simCal
from InputGenerator import get_input, getAnswer
from Parser_me import test_to_STL
from Parser_me import parseJson2STG
from simCal import single_elem_sim

ANS = {}
start_act = {
    'a11': 'acr.browser.lightning.MainActivity8',
    'a12': 'com.ijoysoft.browser.activity.ActivityMain0',
    'a13': 'com.stoutner.privacybrowser.activities.MainWebViewActivity0',
    'a14': 'de.baumann.browser.Activity.BrowserActivity0',
    'a15': 'org.mozilla.focus.activity.MainActivity0',

    'a21': 'com.rubenroy.minimaltodo.MainActivity0',
    'a22': 'douzifly.list.ui.home.MainActivity0',
    'a23': 'org.secuso.privacyfriendlytodolist.view.MainActivity0',
    'a24': 'kdk.android.simplydo.SimplyDoActivity0',
    'a25': 'com.woefe.shoppinglist.activity.MainActivity0',

    'a31': 'com.contextlogic.wish.activity.login.LoginActivity0',
    'a32': 'com.contextlogic.wish.activity.login.createaccount.CreateAccountActivity0',
    'a33': 'com.rainbowshops.activity.ProfileActivity0',
    'a34': '',
    'a35': 'com.yelp.android.nearby.ui.ActivityNearby0',

    'a41': 'com.fsck.k9.activity.MessageList0',
    'a42': 'com.fsck.k9.activity.MessageList0',
    'a43': 'ru.mail.mailapp.MailRuLoginActivity0',
    'a44': 'ru.mail.mailapp.MailRuLoginActivity0',
    'a45': 'ru.mail.ui.SlideStackActivity0',

    'a51': 'anti.tip.tip0',
    'a52': 'com.appsbyvir.tipcalculator.MainActivity0',
    'a53': 'com.tleapps.simpletipcalculator.MainActivity0',
    'a54': 'com.zaidisoft.teninone.Calculator0',
    'a55': 'com.jpstudiosonline.tipcalculator.MainActivity0'
}


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
                        for i in range(len(comp)):
                            idx = int(comp[i]['idx'])
                            MRES[idx] = TGT_ipts[tgt][i]
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
        for i in range(len(path)):
            edges = path[i]
            tmp = []
            elements = edges.target
            if len(elements) > 1:
                for e in elements:
                    if isinstance(e, list):
                        tmp_e = []
                        for k in e:
                            if k['type'] == 'input':
                                tmp_e.append(k)
                            elif k['type'] == 'inputEnter':
                                tmp_e.append(k)
                                # enter = copy.deepcopy(k)
                                # enter['type'] = 'click'
                                # enter['target'] = 'Enter'
                                # STG[s].edges[i].append()
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
    ipts = OrderedDict()
    for s in STG:
        iptElem = []
        state = STG[s]
        key = s
        path = state.edges
        egs = []
        for edges in path:
            elements = edges.target
            for e in elements:
                if isinstance(e, list):
                    if len(e) >= 1:
                        tmp_e = []
                        for k in e:
                            if k['type'] == 'input' or k['type'] == 'inputEnter':
                                if k not in iptElem:
                                    iptElem.append(k)
                # else:
                #     if e['type'] == 'input':
                #         if e not in iptElem:
                #             iptElem.append(e)
        if len(iptElem)>0:
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
    cate = '2'  #设置测试迁移的app种类 （可选1-5，详见data文件夹）
    type = '1'  #设置测试迁移类别(1或2共两类)
    folder = 'a' + cate + '_b' + cate + type #这里设置data文件夹，这里所选的为data/a2_b21
    src = 'a' + cate + '3' #后缀为相应的app，这里所选提供测试的App为a23，其测试见data/a2_b21/a23.json文件
    tgt = 'a' + cate + '1' #后缀为相应的app，这里所选接受测试的App为a21，详见data/a2_b21/tar/a21/activitiesSummary.json文件

    sdir = 'data/' + folder + '/tar/' + src + '/activitiesSummary.json'
    tdir = 'data/' + folder + '/tar/' + tgt + '/activitiesSummary.json'
    test_json = 'data/' + folder + '/' + src + '.json'
    ansjson = 'data/' + folder + '/' + tgt + '.json'

    start_tgt = start_act[tgt]
    # start_tgt = 'com.yelp.android.nearby.ui.ActivityNearby0'
    sim_json = "data/a3_b31/sim_a35.json"
    Init.initAll(sdir, tdir, test_json, sim_json, "a35_a31", start_tgt, folder, src, tgt)

    sg = parseJson2STG(sdir)
    tg = parseJson2STG(tdir)
    file = open(test_json, "rb")
    global test
    test = json.load(file)

    file2 = open(ansjson, "rb")
    ansf = json.load(file2)
    STL = test_to_STL(test, sg)
    STG = tg
    oracle_binding(STL)
    tipt = get_input_from_STG(tg)
    sipt = get_input(STL)
    global MRES
    MRES = initArray(len(test), -1)
    for tmp in tipt:
        find_binds(tmp, tg, tipt)
    ans = getAnswer(ansf)
    ipt_res = exhaustive_search(sipt, tipt, ans, sg, tg)
    ipt_res = sort(ipt_res)
    visited = []
    tgt_paths = []
    SI_paths, IO_paths = STG_pruning(tg, ipt_res, start_tgt)
    SI_path_src, IO_path_src = divide_STL(STL, ipt_res)

    n = 0
    SI_res = {}
    IO_res = {}
    if len(SI_paths) == 0:
        # this means the input is in the initial state
        if len(ipt_res)>0:
            for ipt_key in ipt_res:
                SI_res.update({ipt_key:[0,[],[]]})

    for iop in SI_paths:
        ipt_key = iop[-1].toGraph
        if True:
            score, res = SeqMatcher.seq_match(SI_path_src, iop, STG, ipt_res)
            score = score * SeqMatcher.jump_cost(len(iop), len(SI_path_src) - 1)
            if ipt_key not in SI_res:
                SI_res.update({ipt_key: [score, res, iop]})
            else:
                if score >= SI_res[ipt_key][0]:
                    if score == SI_res[ipt_key][0]:
                        if len(res) > len(SI_res[ipt_key][1]):
                            SI_res.update({ipt_key: [score, res, iop]})
                    else:
                        SI_res.update({ipt_key: [score, res, iop]})
    if len(IO_paths) == 0:
        jump = len(IO_path_src) - 1
        oracle = STL[-1].oracle
        dest = []
        visited = []
        for ipt_key in SI_res:
            ipt_tgt_state = tg[ipt_key]
            states = dfs(ipt_tgt_state, tg, jump + 2)
            for s in states:
                if s not in visited:
                    visited.append(s)
                    if Util.hasElem(oracle, tg[s]):
                        if hasattr(STG[ipt_key], 'binding'):
                            STG[ipt_key].binding.append(s)
                        else:
                            STG[ipt_key].binding = [s]
                        path = Util.getPath(ipt_key, s, [], False)[1]
                        for edgelist in path:
                            if len(edgelist)<jump+2:
                                IO_paths.append(edgelist)

    for iop in IO_paths:
        ipt_key = iop[0].fromGraph
        n += 1
        score, res = SeqMatcher.seq_match(IO_path_src, iop, STG, ipt_res)
        score = score * SeqMatcher.jump_cost(len(iop) - n_ipt_tgt, len(IO_path_src) - n_ipt_src)
        if ipt_key not in IO_res:
            IO_res.update({ipt_key: [score, res, iop]})
        else:
            if score >= IO_res[ipt_key][0]:
                if score == IO_res[ipt_key][0]:
                    if len(res) > len(IO_res[ipt_key][1]):
                        IO_res[ipt_key] = [score, res, iop]
                else:
                    IO_res[ipt_key] = [score, res, iop]

    max = 0
    key_res = ''
    for ikey in ipt_res:
        si_key = ikey
        io_key = ikey
        if ikey in SI_res:
            if len(ipt_res) > 0:
                for k in ipt_res:
                    if k in IO_res:
                        io_key = k
                si_key = ikey
                score_i = SI_res[si_key][0] + IO_res[io_key][0]
                if score_i > max:
                    max = score_i
                    key_res = [si_key, io_key]
    match_res = encode(SI_res, ipt_res, IO_res, key_res, SI_path_src, IO_path_src)
    for r in MRES:
        print(r)


def initArray(l, v):
    a = []
    for i in range(l):
        a.append(v)
    return a


def sort(ipts):
    sorted_ipt = {}
    for n in STG:
        if n in ipts:
            sorted_ipt.update({n: ipts[n]})
    return sorted_ipt


def encode(SI_res, ipt_res, IO_res, key, SI_path_src, IO_path_src):
    res = []
    for i in range(len(SI_path_src)):
        if SI_res[key[0]][1][i] != -1:
            idx = SI_path_src[i].edges[-1]['idx']
            pidx = SI_res[key[0]][1][i]
            paths = SI_res[key[0]][2]
            MRES[idx] = paths[pidx].target[-1]
    for i in range(len(IO_path_src) - 1):
        if IO_res[key[1]][1][i] != -1:
            idx = IO_path_src[i].edges[-1]['idx']
            pidx = IO_res[key[1]][1][i]
            paths = IO_res[key[1]][2]
            evt = paths[pidx].target[-1]
            if isinstance(evt, list):
                evt = evt[-1]
            if evt['type'] != 'input' and 'send_keys' not in test[idx]['action'][0]:
                MRES[idx] = evt
    for i in range(len(MRES)):
        if test[i]['event_type'] == 'oracle':  # case1, disappear
            target = test[i]
            match = {}
            if 'trace_back' in test[i]:
                target = test[i]['trace_back']
            else:
                flag = False
                for j in range(i + 1, len(MRES)):
                    if same(test[j], target):
                        match = copy.deepcopy(MRES[j])
                        if match != -1:  # the oracle's target is matched
                            match['action'] = test[i]['action']
                            flag = True
                            break
                if not flag:
                    if i == len(MRES) - 1:
                        bindings = STG[key[1]].binding
                        for bd in bindings:
                            if bd == IO_res[key[1]][2][-1].toGraph:
                                match['action'] = target['action']
                                match['activity'] = bd
                    else:
                        match = -1
            MRES[i] = match
    return res


def same(e1, e2):
    idf1 = e1['resource-id'] + ' ' + e1['content-desc']
    idf2 = e2['resource-id'] + ' ' + e2['content-desc']
    return idf1 == idf2


def STG_pruning(STG, ipt_matching_res, start_tgt):
    # format description: IO_paths_list = [act]
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
                elem = r_bindings[k][0]
                io_paths_k = Util.getPath(r, k, [])
                e = Edge(elem, 'empty_evt', k, k)
                # io_paths_k[1].append([e)
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
    global n_ipt_tgt
    global n_ipt_src
    ipt_states = []
    for k in res:
        ipts = res[k]
        for i in ipts:
            if i['activity'] not in ipt_states:
                ipt_states.append(i['activity'])
    idx = idxof(STL, ipt_states[0])
    if idx != -1:
        SI_paths = STL[0:idx]
        IO_paths = STL[idx: len(STL)]
    n_ipt_tgt = len(res)
    n_ipt_src = len(ipt_states)
    return SI_paths, IO_paths


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
    visited = []
    for accs in accessble_states:
        if accs not in visited:
            visited.append(accs)
        else:
            continue
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
        # if isNum(st):
        #     if isNum(e.text):
        #         res.append(e)
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


main()

