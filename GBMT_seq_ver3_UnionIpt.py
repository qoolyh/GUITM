import math
from nltk.corpus import wordnet as wn
from itertools import product
import Parser_me
import time
import simCal
from simCal import model
import copy
import numpy
import re
import gensim
from StrUtil import StrUtil
from Edge import Edge
import json

eSim = {}

# model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit= 500000)

'''
def arraySim(strArray, strArray2):
    sum = 0
    for s1 in strArray:
        max = 0
        for s2 in strArray2:
            tmp = wordSim(s1, s2)
            max = max = tmp if tmp > max else max
        sum += max
    if len(strArray) == 0:
        return 0
    return sum / len(strArray)
'''

def w2v_sim(w_from, w_to):
    # w_from = "".join(list(filter(str.isalpha, w_from)))
    # w_to = "".join(list(filter(str.isalpha, w_to)))
    if w_from.lower() == w_to.lower():
        sim = 1.0
    elif w_from in model.vocab and w_to in model.vocab:
        sim = model.similarity(w1=w_from, w2=w_to)
    else:
        sim = 0
    return sim

def arraySim(strArray, strArray2):
    scores = []
    # valid_new_words = []
    # valid_old_words = copy.deepcopy(strArray2)
    valid_new_words = set()
    valid_old_words = set(strArray2)

    for s1 in strArray:
        for s2 in strArray2:
            sim = w2v_sim(s1, s2)
            if sim:
                valid_new_words.add(s1)
                scores.append((s1, s2, sim))
    scores = sorted(scores, key=lambda x: x[2], reverse=True)
    counted = []
    for new_word, old_word, score in scores:
        if new_word in valid_new_words and old_word in valid_old_words:
            valid_new_words.remove(new_word)
            valid_old_words.remove(old_word)
            counted.append(score)
        if not valid_new_words or not valid_old_words:
            break
    # return sum(counted) / len(strArray) if strArray else 0
    return sum(counted) / len(counted) if counted else 0

def wordSim(wordx, wordy):
    sem1, sem2 = wn.synsets(wordx), wn.synsets(wordy)
    maxscore = 0
    for i, j in list(product(*[sem1, sem2])):
        score = i.wup_similarity(j)  # Wu-Palmer Similarity
        if isinstance(score, float):
            maxscore = score if maxscore < score else maxscore
    return maxscore


def haveUpper(str):
    for s in str:
        if s.isupper():
            return True
    return False

'''
def splitByUpper(str):
    res = []
    for k in str.split('_'):
        for s in k.split(' '):
            prev = 0
            flag = False
            for tmpS in s:
                if tmpS.isupper():
                    flag = True
                    tmp = s.find(tmpS)
                    if tmp != prev:
                        res.append(s[prev:tmp])
                        prev = tmp
            if flag:
                res.append(s[prev:len(s)])
            if not flag and not s.isspace() and s != '':
                res.append(s)
    return res
'''

def splitByUpper(str):
    res = []
    p = re.compile(r'([a-z]|\d)([A-Z])')
    for k in str.split('_'):
        for sub in k.split(' '):
            sub = re.sub(p, r'\1_\2', sub).split('_')
            for s in sub:
                prev = 0
                flag = False
                for tmpS in s:
                    if tmpS.isupper():
                        flag = True
                        tmp = s.find(tmpS)
                        if tmp != prev:
                            res.append(s[prev:tmp])
                            prev = tmp
                if flag:
                    res.append(s[prev:len(s)])
                if not flag and not s.isspace() and s != '':
                    res.append(s)
    return res


def similar(str1, str2):
    same = False
    str1_idx = len(str1)
    str2_idx = len(str2)
    for i in range(len(str1) - 1, -1, -1):
        if str1[i].isdigit():
            str1_idx = i
    for i in range(len(str2) - 1, -1, -1):
        if str2[i].isdigit():
            str2_idx = i
    str1 = str1[0:str1_idx]
    str2 = str2[0:str2_idx]
    same = str1 == str2
    return same


def GBTM():
    txtName = "data/" + cate + "/res/" + srcFolder + "_" + tarFolder + '_deleteOutside.txt'
    jsonName = "data/" + cate + "/res/" + srcFolder + "_" + tarFolder + '_deleteOutside.json'
    fileOBJ = open(txtName, 'w', encoding="utf-8")
    start_time = time.time()
    tarIndex = -1
    res = {}
    print("start " + srcFolder + "_" + tarFolder + "_" + cate + "\n")
    fileOBJ.write("start\n")
    prev_elem_info = init_elem_info()
    idxStart = 0
    resultPath = []
    for i in range(len(test_array)):
        # if i == 6:
        #     print("step in")
        if i < idxStart:
            continue
        # should update elem_info after each matching
        if tarIndex != -1 and (i-1) in res:
            match_elem = res[i-1]
            if match_elem != -1:
                prev_elem_info[tar_array[tarIndex]].update({match_elem['resource-id']+'_'+match_elem['bounds'] : 1})
        # modify limit

        score, tmpRes, ind, match_path = graph_match(i - 1, tarIndex, i, 0, 0, copy.deepcopy(prev_elem_info))
        tarIndex = ind
        # print(test_array[i]['resource-id'])
        # print(tarIndex)
        # print(tar_array[tarIndex])
        if match_path:
            resultPath.append(match_path[0])
            lastIptIdx = -1
            tmp = match_path[1:]
            for idx in range(len(tmp)):
                if "action" in test_array[i+idx] and "send_keys" in test_array[i+idx]["action"][0]:
                    lastIptIdx = idx

            if lastIptIdx != -1:
                idxStart = i + lastIptIdx + 2
                tarIndex = tar_array.index(tmp[lastIptIdx].toGraph)
                for idx in range(len(tmp)):
                    if idx <= lastIptIdx:
                        resultPath.append(tmp[idx])

        # print(tmpRes)
        fileOBJ.write(str(tmpRes) + "\n")
        fileOBJ.write(tar_array[tarIndex] + "\n")
        fileOBJ.write("--------------------------------------------------------" + "\n")
        if i - 1 in tmpRes:
            haveMatched[i - 1] = tmpRes[i - 1]
            res[i - 1] = tmpRes[i - 1]
        # break

    end_time = time.time()
    # print('----time:', (end_time-start_time))
    fileOBJ.write('----time:' + str(end_time - start_time) + "\n")

    for k in res:
        if res[k]:
            if isinstance(res[k], list):
                # print("list", " ", test_array[k]['text'], " ", test_array[k]['content-desc'], '.......', k, '.......',
                #       res[k][len(res[k])-1]['text'], " ", res[k][len(res[k])-1]['content-desc'], " ", res[k][len(res[k])-1]['activity'])
                fileOBJ.write(
                    "list" + " " + test_array[k]['text'] + " " + test_array[k]['content-desc'] + '.......' + str(
                        k) + '.......' +
                    res[k][len(res[k]) - 1]['text'] + " " + res[k][len(res[k]) - 1]['content-desc'] + " " +
                    res[k][len(res[k]) - 1]['activity'] + "\n")
            elif not isinstance(res[k], int) and res[k]["type"] == "back":
                fileOBJ.write("BACK_EVENT ......\n")
            elif not isinstance(res[k], int):
                # print(str(test_array[k]['text']), " ", str(test_array[k]['content-desc']), '.......', str(k), '.......',
                #       str(res[k]['text']), " ", str(res[k]['content-desc']), " ", str(res[k]['activity']))
                fileOBJ.write(str(test_array[k]['text']) + " " + str(test_array[k]['content-desc']) + '.......' + str(
                    k) + '.......' +
                              str(res[k]['text']) + " " + str(res[k]['content-desc']) + " " + str(
                    res[k]['activity']) + "\n")
        else:
            # print(test_array[k]['text'], '.......', k, '...as....', 'None')
            fileOBJ.write(test_array[k]['text'] + '.......' + str(k) + '...as....' + 'None' + "\n")

    fileOBJ.write("--------------------------------------------------------" + "\n")

    ground_truth = Parser_me.parse_test_file("data/" + cate + "/" + tarFolder + ".json")
    for j in test_array:
        # print('original.....', j['text'])
        if 'text' in j:
            fileOBJ.write('original.....' + j['text'] + "\n")
        else:
            fileOBJ.write('original.....' + j['action'][0] + "\n")

    fileOBJ.write("--------------------------------------------------------" + "\n")

    for k in ground_truth:
        # print('gnd....', k['text'])
        if 'text' in k:
            fileOBJ.write('gnd....' + k['text'] + "\n")
        else:
            fileOBJ.write('gnd....' + k["action"][0] + "\n")

    fileOBJ.write("--------------------------------------------------------" + "\n")

    fileOBJ.close()

    for i in range(len(resultPath)):
        item = resultPath[i]
        if not isinstance(item, str):
            item = item.toJson()
            resultPath[i] = item
    with open(jsonName, 'w') as f:
        json.dump(resultPath, f)

# def oracle_handler(elem):
#     type = elem.action[0]
#     if type == 'wait_until_element_presence':
#         expect =
def elem_info_to_suffix(graph_info):
    suffix = ''
    for k in graph_info:
        suffix += graph_info[k]
    return suffix


def sim_cal(tar_elem, src_elem, src_graph_idx, tar_graph_id, prev_tgt_elem_info):
    """goal: removes the matched elements in prev_tar_graph, and returns the similar score elem_sim+graph_sim"""
    elem_score = elem_sim(tar_elem, src_elem, prev_tgt_elem_info[tar_graph_id])
    current_tgt_elem_info = copy.deepcopy(prev_tgt_elem_info)
    # graph_sim first, then update the graph
    graph_score = graph_sim_cal(src_graph_idx, tar_graph_id, current_tgt_elem_info)
    current_tgt_elem_info[tar_graph_id].update({tar_elem['resource-id']+'_'+tar_elem['bounds']: 1})
    return graph_score, elem_score, current_tgt_elem_info

'''
def GraphMatch(prev_src, prev_tar, curr_src, steps, tar_elem_matched, prev_tar_elem_info):
    match = -1
    score = 0
    match_info = {}
    resTarIndex = -1

    if steps == step_limit:
        return score, {}, -1
    if curr_src == len(test_array):  # last not match
        return score, {}, -1

    # FOR BACK EVENT
    if 'activity' in test_array[curr_src]:
        curr_src_graph = test_array[curr_src]['activity']
    else:
        curr_src_graph = test_array[prev_src]['activity']

    # at the beginning
    if prev_src == -1:
        for i in range(len(tar_array)):
            elem_info = numpy.zeros(len(tar_dict[tar_array[i]].elems))
            current_tar_elem_info = init_elem_info(tar_array[i])
            graph_sim = calculateGraphSim(curr_src, tar_array[i])
            next_score, next_match, _ = GraphMatch(curr_src, i, curr_src + 1, steps + 1,
                                                   copy.deepcopy(tar_elem_matched), current_tar_elem_info)
            res = graph_sim + next_score
            if res >= score:
                score = res
                match_info = {prev_src: None}
                match_info.update(next_match)
                resTarIndex = i
        return score, match_info, resTarIndex

    # at the internal
    else:
        if 'activity' in test_array[prev_src]:
            prev_src_graph = test_array[prev_src]['activity']
        else:
            prev_src_graph = test_array[prev_src - 1]['activity']
        step_src = 0 if similar(curr_src_graph, prev_src_graph) else 1
        next_match_info = {}
        for i in range(len(tar_array)):
            # if prev_src == 0 and i == 13:
            #     print("1")
            tar_graph = tar_dict[tar_array[i]]
            # graph_sim = graph_sim_matrix[curr_src_graph + ' ' + tar_array[i]]
            graph_sim = calculateGraphSim(curr_src, tar_array[i])
            # if graph_sim <= 0.2:
            #     continue
            e_match = -1
            src_elem = test_array[prev_src]
            # case 1, foraging from internal edges (point to itself)
            if i == prev_tar:
                matching_score = 0
                for tar_edge in tar_graph.edges:
                    if tar_edge.toGraph == tar_edge.fromGraph:
                        for tar_elem in tar_edge.target:
                            step_tar = 0
                            step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
                            # if abs(step_tar - step_src) == 1:
                            #     step_cost = 1
                            tmp_score = graph_sim / step_cost + elemSim(tar_elem, src_elem, tar_elem_matched,
                                                                        tar_edge.fromGraph)
                            if matching_score <= tmp_score:
                                matching_score = tmp_score
                                e_match = tar_elem
                                if isinstance(tar_elem, list):
                                    e_match[len(tar_elem) - 1]["activity"] = tar_edge.fromGraph
                                else:
                                    e_match["activity"] = tar_edge.fromGraph

            # case 2, foraging from external edges (point to other graphs)
            else:
                connect, path = getPath(prev_tar, i, adjacent_matrix_tar, [])
                matching_score = 0
                if connect or i == prev_tar:
                    for p in path:
                        step_tar = len(p)
                        if step_tar >= 3:
                            continue
                        step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
                        e_sim, tar_match = evt_sim(p, prev_src, tar_elem_matched)
                        tmp_score = graph_sim / step_cost + e_sim
                        if tmp_score >= matching_score:
                            matching_score = tmp_score
                            e_match = tar_match

            # matched改成prev和cur为键
            if e_match == -1:
                continue
            new_matched = updateMatched(copy.deepcopy(e_match), copy.deepcopy(tar_elem_matched))
            next_score, next_match, _ = GraphMatch(curr_src, i, curr_src + 1, steps + 1, copy.deepcopy(new_matched))
            matching_score += next_score
            # if prev_tar ==  13 and prev_src == 1 and i == 13:
            #     print(matching_score)
            # if prev_tar ==  13 and prev_src == 1 and i == 29:
            #     print(matching_score)

            if score <= matching_score:
                score = matching_score
                match = e_match
                next_match_info = next_match
                # if prev_src == 0 and curr_src == 1 and e_match == -1:
                #     b = 1
                resTarIndex = i
                if prev_src == 0:
                    a = 1

        # after foraging, return the result: {prev_src:match}+next_match_info
        match_info = {prev_src: match}
        match_info.update(next_match_info)
        # if prev_src == 1 and match == -1 and 'activity' in next_match and next_match["activity"] == "'com.contextlogic.wish.activity.search.SearchActivity1'":
        #     a = 1
        return score, match_info, resTarIndex
'''

def graph_match(prev_src_idx, prev_tar_idx, curr_src_idx, steps, count, prev_tar_elem_info):
    match = -1
    match_graph_id = ''
    score = 0
    match_info = {}
    resTarIndex = -1
    match_path = []

    if steps == step_limit:
        return score, {}, -1, []
    if count == max_step_limit:
        return score, {}, -1, []
    if curr_src_idx == len(test_array):  # last not match
        return score, {}, -1, []

    # FOR BACK EVENT
    if 'activity' in test_array[curr_src_idx]:
        curr_src_graph = test_array[curr_src_idx]['activity']
    else:
        curr_src_graph = test_array[prev_src_idx]['activity']

    # at the beginning
    if prev_src_idx == -1:
        current_tar_elem_info = prev_tar_elem_info
        for i in range(len(tar_array)):
            # if i <= 21 or i >= 66:
            #     continue
            graph_sim = calculateGraphSim(curr_src_idx, tar_array[i])
            if graph_sim == 0:
                continue
            next_score, next_match, _, next_match_path = graph_match(curr_src_idx, i, curr_src_idx + 1, steps + 1, count + 1, current_tar_elem_info)
            res = graph_sim + next_score

            if res > score:
                score = res
                match_info = {prev_src_idx: None}
                match_info.update(next_match)
                resTarIndex = i
                match_path = ["-1"] + next_match_path
        return score, match_info, resTarIndex, match_path

    # at the internal
    else:
        e_match = -1
        current_tgt_elem_info = prev_tar_elem_info
        if 'activity' in test_array[prev_src_idx]:
            prev_src_graph = test_array[prev_src_idx]['activity']
        else:
            prev_src_graph = test_array[prev_src_idx - 1]['activity']
        step_src = 0 if similar(curr_src_graph, prev_src_graph) else 1
        next_match_info = {}
        key = 'com.contextlogic.wish.activity.login.signin.SignInActivity0'
        if key not in prev_tar_elem_info:
            a=1
            # print(a)
        for i in range(len(tar_array)):
            e_match = -1
            pathStore = []
            # if i <= 21 or i >= 66:
            #     continue
            curr_sim = 0
            tar_graph_id = tar_array[i]
            tar_graph = tar_dict[tar_graph_id]
            src_elem = test_array[prev_src_idx]
            # case 1, foraging from internal edges (point to itself)
            if i == prev_tar_idx:
                matching_score = 0
                for tar_edge in tar_graph.edges:
                    if tar_edge.toGraph == tar_edge.fromGraph:
                        step_tar = 0
                        step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
                        for evt in tar_edge.target:
                            edge = Edge(evt, tar_edge.event , tar_edge.fromGraph, tar_edge.toGraph)
                            if isinstance(evt, list):
                                for tar_elems in evt:
                                    if isinstance(tar_elems, list):
                                        for tar_elem in tar_elems:
                                            graph_score, elem_score, current_tgt_elem_info_tmp = sim_cal(tar_elem,
                                                                                                         src_elem,
                                                                                                         curr_src_idx,
                                                                                                         tar_graph_id,
                                                                                                         prev_tar_elem_info
                                                                                                         )
                                            if graph_score == 0:
                                                continue
                                            tmp_score = graph_score / step_cost + elem_score / step_cost
                                            if curr_sim <= tmp_score:
                                                current_tgt_elem_info = current_tgt_elem_info_tmp
                                                curr_sim = tmp_score
                                                e_match = tar_elem
                                                if isinstance(tar_elem, list):
                                                    e_match[len(tar_elem) - 1]["activity"] = tar_edge.fromGraph
                                                else:
                                                    e_match["activity"] = tar_edge.fromGraph
                                                pathStore = [edge]
                                    else:
                                        tar_elem = tar_elems
                                        graph_score, elem_score, current_tgt_elem_info_tmp = sim_cal(tar_elem,
                                                                                                     src_elem,
                                                                                                     curr_src_idx,
                                                                                                     tar_graph_id,
                                                                                                     prev_tar_elem_info
                                                                                                     )
                                        if graph_score == 0:
                                            continue
                                        tmp_score = graph_score / step_cost + elem_score / step_cost
                                        if curr_sim <= tmp_score:
                                            current_tgt_elem_info = current_tgt_elem_info_tmp
                                            curr_sim = tmp_score
                                            if elem_score != 0:
                                                e_match = tar_elem
                                                if isinstance(tar_elem, list):
                                                    e_match[len(tar_elem) - 1]["activity"] = tar_edge.fromGraph
                                                else:
                                                    e_match["activity"] = tar_edge.fromGraph
                                                pathStore = [edge]
                            else:
                                tar_elems = evt
                                if isinstance(tar_elems, list):
                                    for tar_elem in tar_elems:
                                        graph_score, elem_score, current_tgt_elem_info_tmp = sim_cal(tar_elem,
                                                                                                         src_elem,
                                                                                                         curr_src_idx,
                                                                                                         tar_graph_id,
                                                                                                         prev_tar_elem_info
                                                                                                         )
                                        if graph_score == 0:
                                            continue
                                        tmp_score = graph_score / step_cost + elem_score / step_cost
                                        if curr_sim <= tmp_score:
                                            current_tgt_elem_info = current_tgt_elem_info_tmp
                                            curr_sim = tmp_score
                                            if elem_score != 0:
                                                e_match = tar_elem
                                                if isinstance(tar_elem, list):
                                                    e_match[len(tar_elem) - 1]["activity"] = tar_edge.fromGraph
                                                else:
                                                    e_match["activity"] = tar_edge.fromGraph
                                                pathStore = tar_elems
                                else:
                                    tar_elem = tar_elems
                                    graph_score, elem_score, current_tgt_elem_info_tmp = sim_cal(tar_elem,
                                                                                                 src_elem,
                                                                                                 curr_src_idx,
                                                                                                 tar_graph_id,
                                                                                                 prev_tar_elem_info
                                                                                                 )
                                    if graph_score == 0:
                                        continue
                                    tmp_score = graph_score / step_cost + elem_score / step_cost
                                    if curr_sim <= tmp_score:
                                        current_tgt_elem_info = current_tgt_elem_info_tmp
                                        curr_sim = tmp_score
                                        if elem_score != 0:
                                            e_match = tar_elem
                                            if isinstance(tar_elem, list):
                                                e_match[len(tar_elem) - 1]["activity"] = tar_edge.fromGraph
                                            else:
                                                e_match["activity"] = tar_edge.fromGraph
                                            pathStore = [edge]
            # case 2, foraging from external edges (point to other graphs)
            else:
                connect, path = getPath(prev_tar_idx, i, adjacent_matrix_tar, [])
                if connect or i == prev_tar_idx:
                    for p in path:
                        step_tar = len(p)
                        if step_tar > 1:
                            continue
                        step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
                        graph_score, elem_score, match_elem, current_tgt_elem_info_tmp = sim_cal_edge_ver(p, src_elem,
                                                                                                          curr_src_idx,
                                                                                                          prev_tar_elem_info,
                                                                                                          tar_graph_id)
                        if graph_score == 0:
                            continue
                        tmp_score = graph_score / step_cost + elem_score / step_cost
                        if curr_sim <= tmp_score:
                            curr_sim = tmp_score
                            if elem_score != 0:
                                e_match = match_elem
                                current_tgt_elem_info = current_tgt_elem_info_tmp
                                pathStore = p

            if e_match == -1:
                continue
            if "action" in src_elem and "send_keys" in src_elem["action"][0]:
                next_score, next_match, _, next_match_path = graph_match(curr_src_idx, i, curr_src_idx + 1, steps, count + 1,
                                                        copy.deepcopy(current_tgt_elem_info))
            else:
                next_score, next_match, _, next_match_path = graph_match(curr_src_idx, i, curr_src_idx + 1, steps + 1, count + 1,
                                                        copy.deepcopy(current_tgt_elem_info))
            curr_sim += next_score
            if score < curr_sim:
                score = curr_sim
                match = e_match
                next_match_info = next_match
                resTarIndex = i
                match_path = pathStore + next_match_path
                if prev_src_idx == 0:
                    a = 1
        match_info = {prev_src_idx: match}
        match_info.update(next_match_info)

        return score, match_info, resTarIndex, match_path


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


'''
def evt_sim(path, prev_src, matched):
    """path is a set of edges from prev_tar to current_tar"""
    se = None if prev_src == -1 else test_array[prev_src]  # get src from test_array
    score = 0
    match_elem = None
    for i in range(len(path)):
        events = path[i].target
        for e in events:
            if prev_src in haveMatched:
                return elemSim(haveMatched[prev_src], se, matched, path[i].fromGraph), haveMatched[prev_src]
            v = elemSim(e, se, matched, path[i].fromGraph)
            if v >= score:
                score = v
                match_elem = e
                if isinstance(e, list):
                    match_elem[len(e) - 1]["activity"] = path[i].fromGraph
                else:
                    match_elem["activity"] = path[i].fromGraph
    return score, match_elem
'''

def sim_cal_edge_ver(tar_edge_list, src_elem, src_graph_idx, prev_tgt_elem_info, current_tgt_graph_id):
    """goal: removes the matched elements in prev_tar_graph, and returns the similar score elem_sim+graph_sim"""
    score = 0
    match_elem = None
    match_graph = ''
    for i in range(len(tar_edge_list)):
        events = tar_edge_list[i].target
        tgt_graph_id = tar_edge_list[i].fromGraph
        for tar_elem in events:
            if isinstance(tar_elem, list):
                for t_elem in tar_elem:
                    elem_score = elem_sim(t_elem, src_elem, prev_tgt_elem_info[tgt_graph_id])
                    if elem_score >= score:
                        score = elem_score
                        match_graph = tgt_graph_id
                        match_elem = t_elem
                        match_elem["activity"] = tgt_graph_id
                # t_elem = tar_elem[len(tar_elem) - 1]
                # elem_score = elem_sim(t_elem, src_elem, prev_tgt_elem_info[tgt_graph_id])
                # if elem_score >= score:
                #     score = elem_score
                #     match_graph = tgt_graph_id
                #     match_elem = t_elem
                #     match_elem["activity"] = tgt_graph_id

            else:
                elem_score = elem_sim(tar_elem, src_elem, prev_tgt_elem_info[tgt_graph_id])
                if elem_score >= score:
                    score = elem_score
                    match_graph = tgt_graph_id
                    match_elem = tar_elem
                    match_elem["activity"] = tgt_graph_id

    current_tgt_elem_info = copy.deepcopy(prev_tgt_elem_info)
    graph_score = graph_sim_cal(src_graph_idx, current_tgt_graph_id, current_tgt_elem_info)
    if match_elem is not None:
        if match_elem['type'] == "back":
            key = "back_none"
        else:
            key = str(match_elem['resource-id']+'_'+match_elem['bounds'])
        current_tgt_elem_info[match_graph].update({key:1})
    return graph_score, score, match_elem, current_tgt_elem_info


def elem_sim(tgt_elem, src_elem, prev_tgt_elem_info):
    if not src_elem:
        return 0
    length = 0
    if not isinstance(tgt_elem, list) and tgt_elem["type"] == "back":
        if src_elem["event_type"] == "SYS_EVENT" and src_elem["action"][0] == "KEY_BACK":
            return 1
        else:
            return 0
    if src_elem["action"][0] == "KEY_BACK":
        return 0
    tgt_id = ""
    tgt_key = ''
    if isinstance(tgt_elem, list):
        # print('1111111111------------')
        length = len(tgt_elem)
        if tgt_elem[length - 1]['resource-id'].find("/") != -1:
            tgt_id = tgt_elem[length - 1]['resource-id'].split("/")[1]
        else:
            tgt_id = tgt_elem[length - 1]['resource-id']
        key = str('tar' + tgt_id + ' ' + tgt_elem[length - 1]['index']) + "_" + str(src_elem['id'] + "_list")
        tgt_key = tgt_elem[length - 1]['resource-id']+'_'+tgt_elem[length - 1]['bounds']
    else:
        if tgt_elem['resource-id'].find("/") != -1:
            tgt_id = tgt_elem['resource-id'].split("/")[1]
        else:
            tgt_id = tgt_elem['resource-id']
        key = str('tar' + tgt_id + ' ' + tgt_elem['index']) + "_" + str(src_elem['id'])
        tgt_key = tgt_elem['resource-id']+'_'+tgt_elem['bounds']
    if (tgt_elem['resource-id'] == 'com.contextlogic.geek:id/create_wishlist_name_text'):
        a=1
    src_id = src_elem['id']
    if length == 0:
        tgt_txt = tgt_elem['text']
        tgt_cls = tgt_elem['class']
        tgt_desc = tgt_elem['content-desc']
    else:
        tgt_txt = tgt_elem[length - 1]['text']
        tgt_cls = tgt_elem[length - 1]['class']
        tgt_desc = tgt_elem[length - 1]['content-desc']
    if prev_tgt_elem_info[tgt_key] == 1:
        return 0
    if key in eSim:
        return eSim[key]
    else:
        src_txt = src_elem['text']
        src_cls = src_elem['class']
        src_desc = src_elem['content-desc']

        if src_id == "edit_text" and tgt_id == "newTodoTimeEditText":
            a = 1
        if src_id == "edit_text" and tgt_id == "userToDoEditText":
            b = 1
        # contentScore = arraySim(splitByUpper(tgt_txt), splitByUpper(src_txt))
        # idScore = arraySim(splitByUpper(str(tgt_id)), splitByUpper(str(src_id)))
        # clsScore = arraySim(splitByUpper(str(tgt_cls)), splitByUpper(str(src_cls)))
        clsMatch = False
        for key in StrUtil.CLASS_CATEGORY:
            if key in src_cls.lower():
                for cls in StrUtil.CLASS_CATEGORY[key]:
                    if cls in tgt_cls.lower():
                        clsMatch = True
                        break
                if clsMatch:
                    break
        # if src_cls in StrUtil.CLASS_CATEGORY:
        #     if tgt_cls in StrUtil.CLASS_CATEGORY[src_cls]:
        #         clsMatch = True
        # descScore = arraySim(splitByUpper(str(tgt_desc)), splitByUpper(str(src_desc)))
        contentScore = arraySim(StrUtil.tokenize("text", tgt_txt), StrUtil.tokenize("text", src_txt))
        if tgt_id == "button1":
            a = 1
        idScore = arraySim(StrUtil.expand_text(tgt_cls, "resource-id", StrUtil.tokenize("resource-id", tgt_id)),
                           StrUtil.expand_text(src_cls, "resource-id", StrUtil.tokenize("resource-id", src_id)))

        descScore = arraySim(StrUtil.tokenize("content-desc", tgt_desc), StrUtil.tokenize("content-desc", src_desc))
        v = contentScore + idScore + descScore# + clsScore
        v /= 3

        if not clsMatch:
            v -= 0.5

        eSim.update({key: v})
    return v


def init_elem_info():
    tar_elem_info = {}
    for i in range(len(tar_array)):
        tar_graph = tar_dict[tar_array[i]]
        elem_info = {}
        for e in tar_graph.elements:
            id = e.id+'_'+e.bounds
            elem_info.update({id: 0})
            if ('com.contextlogic.geek:id/create_wishlist_name_text' == e.id):
                a = 1
        tar_elem_info.update({tar_array[i]:elem_info})
    if ('com.contextlogic.geek:id/create_wishlist_name_text_[144,887][363,938]' in tar_elem_info):
        a = 1
    else:
        b = 1
    return tar_elem_info

'''
def elemSim(e, se, matched, act):
    if not se:
        return 0
    length = 0
    if not isinstance(e, list) and e["type"] == "back":
        if se["event_type"] == "SYS_EVENT" and se["action"][0] == "KEY_BACK":
            return 1
        else:
            return 0
    if se["action"][0] == "KEY_BACK":
        return 0
    tid = ""
    if isinstance(e, list):
        length = len(e)
        if e[length - 1]['resource-id'].find("/") != -1:
            tid = e[length - 1]['resource-id'].split("/")[1]
        else:
            tid = e[length - 1]['resource-id']
        key = str('tar' + tid + ' ' + e[length - 1]['index']) + "_" + str(se['id'] + "_list")
    else:
        if e['resource-id'].find("/") != -1:
            tid = e['resource-id'].split("/")[1]
        else:
            tid = e['resource-id']
        key = str('tar' + tid + ' ' + e['index']) + "_" + str(se['id'])

    sid = se['id']
    if length == 0:
        tid = tid
        ttxt = e['text']
        tcls = e['class']
        tdesc = e['content-desc']
    else:
        tid = tid
        ttxt = e[length - 1]['text']
        tcls = e[length - 1]['class']
        tdesc = e[length - 1]['content-desc']

    if act in matched:
        eKey = tid + "->" + ttxt + "->" + tcls + "->" + tdesc
        if eKey in matched[act]:
            return 0

    if key in eSim:
        return eSim[key]
    else:

        sid = sid
        stxt = se['text']
        scls = se['class']
        sdesc = se['content-desc']

        contentScore = arraySim(splitByUpper(ttxt), splitByUpper(stxt))
        idScore = arraySim(splitByUpper(str(tid)), splitByUpper(str(sid)))
        clsScore = arraySim(splitByUpper(str(tcls)), splitByUpper(str(scls)))
        descScore = arraySim(splitByUpper(str(tdesc)), splitByUpper(str(sdesc)))
        v = contentScore + idScore + descScore + clsScore
        v /= 4

        eSim.update({key: v})

    return v
'''

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


def get_edge(from_graph_idx, to_graph_idx):
    edge = None
    edges = tar_dict[tar_array[from_graph_idx]].edges
    for e in edges:
        if e.toGraph == tar_array[to_graph_idx]:
            edge = e
            break
    return edge


def getPath(fromGraph, toGraph, am, visited):
    if fromGraph == -1:
        return True, []
    visited.append(fromGraph)
    connect = am[fromGraph][toGraph] == 1
    way = []
    if connect:
        way.append([get_edge(fromGraph, toGraph)])
    for i in range(len(am)):
        if am[fromGraph][i] == 1 and i not in visited:
            tmp, ways = getPath(i, toGraph, am, visited)
            if tmp:
                connect = tmp
                for tmpPath in ways:
                    if tmpPath:
                        newPath = [get_edge(fromGraph, i)]
                        newPath.extend(tmpPath)
                        way.append(newPath)
    return connect, way


cache = {}

def calculateGraphSim(test_idx, tar_id):
    # test_node = test_array[test_idx]
    # if 'activity' not in test_node:
    #     test_node = test_array[test_idx - 1]
    # src_activity = test_node['activity']
    # src_graph_elems = src_dict[src_activity].elements
    src_graph_elems = src_elem_dicts_minus[test_idx]
    tar_graph_elems = tar_dict[tar_id].elements
    key = str(test_idx) + "_" + str(tar_id)
    if key in cache:
        return cache[key]
    # for i in range(test_idx + 1):
    #     node = test_array[i]
    #     if 'activity' not in node:
    #         node = test_array[i - 1]
    #     toDeleteElem = {"id": node["resource-id"], "class": node["class"]}
    #     src_graph_elems = deleteElem(src_graph_elems, toDeleteElem)

    # v = simCal.graphSim_TFIDF(src_graph_elems, tar_graph_elems)
    v = simCal.graphSim_TFIDF(src_graph_elems, tar_graph_elems)
    cache[key] = v
    return v


def graph_sim_cal(src_graph_idx, current_tgt_graph_id, current_tgt_elem_info):
    # src_graph = test_array[src_graph_idx]
    # if 'activity' not in src_graph:
        # src_graph = test_array[src_graph_idx - 1]
    # src_activity = src_graph['activity']
    src_graph_elems = src_elem_dicts_minus[src_graph_idx]
    # src_graph_elems = src_dict[src_activity].elements
    tar_graph_elems_candidate = tar_dict[current_tgt_graph_id].elements
    tar_graph_elems = []
    suffix = ''
    for i in range(len(tar_graph_elems_candidate)):
        this_elem_info = current_tgt_elem_info[current_tgt_graph_id][tar_graph_elems_candidate[i].id+'_'+tar_graph_elems_candidate[i].bounds]
        suffix += str(this_elem_info)
        if this_elem_info == 0:  # 0 means the element has not been matched
            tar_graph_elems.append(tar_graph_elems_candidate[i])
    if (src_graph_idx == 1 and current_tgt_graph_id == "com.yelp.android.ui.activities.ActivityCreateAccount2"):
        a = 1
    key = str(src_graph_idx) + "_" + str(current_tgt_graph_id) + '_' + suffix
    if key in cache:
        return cache[key]
    # toDeleteElem = {"id": src_graph["resource-id"], "class": src_graph["class"]}
    # src_graph_elems = deleteElem(src_graph_elems, toDeleteElem)
    # v = simCal.graphSim_TFIDF(src_graph_elems, tar_graph_elems)
    v = simCal.graphSim_TFIDF(src_graph_elems, tar_graph_elems)
    cache[key] = v
    return v


def deleteElem(graph, elem):
    graph = copy.deepcopy(graph)
    elemId = elem["id"]
    for idx in range(len(graph)):
        eID = graph[idx].id if graph[idx].id.find("/") == -1 else graph[idx].id.split("/")[1]
        if eID == elemId:
            graph.pop(idx)
            break
    return graph

def initSrcDict():
    src_elem_dicts_minus = []
    for i in range(len(test_array)):
        if "activity" not in test_array[i]:
            test_array[i]["activity"] = test_array[i - 1]["activity"]

    for i in range(len(test_array)):
        curr_idx = i
        prev_idx = i - 1
        if curr_idx == 0:
            src_elem_dicts_minus.append(src_dict[test_array[curr_idx]["activity"]].elements)
        else:
            if "activity" not in test_array[curr_idx] or test_array[prev_idx]["activity"] == test_array[curr_idx]["activity"]:
                elems = deleteElem(src_elem_dicts_minus[prev_idx], test_array[prev_idx])
                src_elem_dicts_minus.append(elems)
            else:
                elems = src_dict[test_array[curr_idx]["activity"]].elements
                src_elem_dicts_minus.append(elems)
    return src_elem_dicts_minus

graphSim = [[0.3184, 0.1477, 0.1755, 0.1761],
            [0.2091, 0.1506, 0.1752, 0.208],
            [0.217, 0.1662, 0.1727, 0.2422],
            [0.2123, 0.1926, 0.2291, 0.1879],
            [0.2258, 0.2743, 0.2649, 0.2371],
            [0.2338, 0.2195, 0.2428, 0.2232],
            ]

srcGroups = [
             ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a31', 'a32', 'a33', 'a35'],
             ['a31', 'a32', 'a33', 'a35'],
             ['a41', 'a42', 'a43', 'a44', 'a45'],
             ['a41', 'a42', 'a43', 'a44', 'a45'],
             ['a51', 'a52', 'a53', 'a54', 'a55'],
             ['a51', 'a52', 'a53', 'a54', 'a55']
             ]
tarGroups = [
             ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a31', 'a32', 'a33', 'a35'],
             ['a31', 'a32', 'a33', 'a35'],
             ['a41', 'a42', 'a43', 'a44', 'a45'],
             ['a41', 'a42', 'a43', 'a44', 'a45'],
             ['a51', 'a52', 'a53', 'a54', 'a55'],
             ['a51', 'a52', 'a53', 'a54', 'a55']
             ]
srcFolder = ''
tarFolder = ''
cates = [
         'a1_b11',
         'a1_b12',
         # 'a2_b21',
         'a2_b22',
         'a3_b31',
         'a3_b32',
         'a4_b41',
         'a4_b42',
         'a5_b51',
         'a5_b52'
        ]
cate = ''
srcGroup = ''
tarGroup = ''
haveMatched = {}
for i in range(len(cates)):
    cate = cates[i]
    srcGroup = srcGroups[i]
    tarGroup = tarGroups[i]
    haveMatched = {}
    for src in srcGroup:
        # if src != 'a31':
        #     continue
        srcFolder = src
        for tar in tarGroup:
            tarFolder = tar
            # if tar != 'a35':
            #     continue
            if src != tar:
                haveMatched = {}
                pair = src + '_' + tar
                # pair = 'a31_a35'
                sim_json = "data/" + cate + "/sim_" + src + ".json"
                # sim_json = "data/sim_a31.json"
                src_json = "data/" + cate + "/src/" + src + "/activitiesSummary.json"
                # src_json = "data/src/a31/activitiesSummary.json"
                tar_json = "data/" + cate + "/tar/" + tar + "/activitiesSummary.json"
                # tar_json = "data/tar/a35/activitiesSummary.json"
                test_json = "data/" + cate + "/" + src + ".json"

                src_dict = Parser_me.parseJson2STG(src_json)
                tar_dict = Parser_me.parseJson2STG(tar_json)
                src_array = Parser_me.dict2array(src_dict)
                tar_array = Parser_me.dict2array(tar_dict)

                graph_sim_matrix = Parser_me.parse_graph_json(sim_json)[pair]
                adjacent_matrix_tar = Parser_me.getAM(tar_dict)
                test_array = Parser_me.parse_test_file(test_json)
                step_limit = 2
                max_step_limit = 5
                src_elem_dicts_minus = initSrcDict()
                GBTM()
