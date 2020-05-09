import math
from nltk.corpus import wordnet as wn
from itertools import product
import Parser_me
import time
import copy
from Edge import Edge

MIN=0

def arraySim(strArray, strArray2):
    sum = 0
    for s1 in strArray:
        max = 0
        for s2 in strArray2:
            tmp = wordSim(s1, s2)
            max = max = tmp if tmp > max else max
        sum += max
    if len(strArray) == 0 and len(strArray2) != 0:
        return 0
    elif len(strArray) == 0 and len(strArray2) == 0:
        return 1
    return sum / len(strArray)


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
    fileOBJ = open("data/a1_b11/" + srcFolder + "_" + tarFolder + '.txt', 'w')
    start_time = time.time()
    tarIndex = -1
    res = {}
    print("start " + srcFolder + "_" + tarFolder)
    fileOBJ.write("start\n")
    for i in range(len(test_array)):
        score, tmpRes, ind = GraphMatch(i - 1, tarIndex, i, 0)
        tarIndex = ind
        fileOBJ.write(str(tmpRes) + "\n")
        fileOBJ.write(tar_array[tarIndex] + "\n")
        fileOBJ.write("--------------------------------------------------------" + "\n")
        if i == 0:
            continue
        res[i - 1] = tmpRes[i - 1]
    end_time = time.time()
    fileOBJ.write('----time:' + str(end_time - start_time) + "\n")

    for k in res:
        if res[k]:
            if isinstance(res[k], list):
                fileOBJ.write(
                    "list" + " " + test_array[k]['text'] + " " + test_array[k]['content-desc'] + '.......' + str(
                        k) + '.......' +
                    res[k][len(res[k]) - 1]['text'] + " " + res[k][len(res[k]) - 1]['content-desc'] + " " +
                    res[k][len(res[k]) - 1]['activity'] + "\n")
            elif not isinstance(res[k], int):
                fileOBJ.write(str(test_array[k]['text']) + " " + str(test_array[k]['content-desc']) + '.......' + str(
                    k) + '.......' +
                              str(res[k]['text']) + " " + str(res[k]['content-desc']) + " " + str(
                    res[k]['activity']) + "\n")
        else:
            fileOBJ.write(test_array[k]['text'] + '.......' + str(k) + '...as....' + 'None' + "\n")

    fileOBJ.write("--------------------------------------------------------" + "\n")

    ground_truth = Parser_me.parse_test_file("data/a1_b11/" + tarFolder + ".json")
    for j in test_array:
        # print('original.....', j['text'])
        fileOBJ.write('original.....' + j['text'] + "\n")

    fileOBJ.write("--------------------------------------------------------" + "\n")

    for k in ground_truth:
        fileOBJ.write('gnd....' + k['text'] + "\n")

    fileOBJ.write("--------------------------------------------------------" + "\n")
    fileOBJ.close()





def GraphMatch(prev_src, prev_tar, curr_src, steps):
    match = -1
    score = 0
    match_info = {}
    resTarIndex = -1
    if steps == 3:
        return score, {}, -1
    if curr_src == len(test_array):  # last not match
        return score, {}, -1

    # 改test json，这里肯定不能这么写
    curr_src_graph = test_array[curr_src]['activity']

    # at the beginning
    if prev_src == -1:
        for i in range(len(tar_array)):
            # if i == 13 or i == 22 or i == 42:
            #     print("1")
            graph_sim = graph_sim_matrix[curr_src_graph + ' ' + tar_array[i]]
            if graph_sim == 0:
                continue
            next_score, next_match, _ = GraphMatch(curr_src, i, curr_src + 1, steps + 1)
            res = graph_sim + next_score
            if res >= score:
                score = res
                match_info = {prev_src: None}
                match_info.update(next_match)
                resTarIndex = i
        return score, match_info, resTarIndex
    # at the internal
    else:
        prev_src_graph = test_array[prev_src]['activity']
        step_src = 0 if similar(curr_src_graph, prev_src_graph) else 1
        next_match_info = {}
        for i in range(len(tar_array)):
            # if i == 22 or i == 42:
            #     print("1")
            tar_graph = tar_dict[tar_array[i]]
            graph_sim = graph_sim_matrix[curr_src_graph + ' ' + tar_array[i]]
            if graph_sim == 0:
                continue
            next_score, next_match, _ = GraphMatch(curr_src, i, curr_src + 1, steps + 1)
            src_elem = test_array[prev_src]
            # case 1, foraging from internal edges (point to itself)
            if i == prev_tar:
                for tar_edge in tar_graph.edges:
                    if tar_edge.toGraph == tar_edge.fromGraph:
                        for tar_elem in tar_edge.target:
                            step_tar = 0
                            step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
                            # if abs(step_tar - step_src) == 1:
                            #     step_cost = 1
                            matching_score = graph_sim / step_cost + next_score + elemSim(tar_elem, src_elem)
                            if score <= matching_score:
                                score = matching_score
                                match = tar_elem
                                if isinstance(tar_elem, list):
                                    match[len(tar_elem) - 1]["activity"] = tar_edge.fromGraph
                                else:
                                    match["activity"] = tar_edge.fromGraph
                                next_match_info = next_match
                                resTarIndex = i
            # case 2, foraging from external edges (point to other graphs)
            else:
                connect, path = getPath(prev_tar, i, adjacent_matrix_tar, [])
                if connect or i == prev_tar:
                    for p in path:
                        step_tar = len(p)
                        step_cost = math.log(abs(step_tar - step_src) + 1, 2) + 1
                        e_sim, e_match = evt_sim(p, prev_src)
                        matching_score = graph_sim / step_cost + next_score + e_sim
                        if score <= matching_score:
                            score = matching_score
                            match = e_match
                            next_match_info = next_match
                            resTarIndex = i
        # after foraging, return the result: {prev_src:match}+next_match_info
        match_info = {prev_src: match}
        match_info.update(next_match_info)
        return score, match_info, resTarIndex


# def traverse_graph_ver(graph_idx, step, adjacent_matrix_tar):
#     graph_list = []
#     node_list = []
#     graph_set = {}
#     if step == 1:
#         list.append(graph_idx)
#         graph_set[step] = [list]
#     else:
#         prev_graph_set = traverse(graph_idx, step - 1, adjacent_matrix_tar)
#         prev_list = prev_graph_set[step - 1]
#         for i in prev_list:
#             prev_graph = i
#             current_graph = prev_graph[len(prev_graph) - 1]
#             next_idx = []
#             for j in range(len(adjacent_matrix_tar)):
#                 if adjacent_matrix_tar[current_graph][j] == 1 and current_graph != j:
#                     next.append(j)
#             for k in next:
#                 clone_prev_graphs = copy.deepcopy(prev_graph)
#                 clone_prev_graphs.append(k)
#                 list.append(clone_prev_graphs)
#         graph_set = prev_graph_set
#         graph_set[step] = list
#     return graph_set


def traverse(tgt_graph_id, step, tgt_graph_dict):
    list = []
    edgeSet = {}
    if step == 1:
        for edge in tgt_graph_dict[tgt_graph_id].edges:
            tmp = []
            tmp.append(edge)
            list.append(tmp)
        edgeSet[step] = list
    else:
        prevEdgeSet = traverse(tgt_graph_id, step - 1, tgt_graph_dict)
        prevList = prevEdgeSet[step - 1]
        for i in prevList:
            prevEdges = i
            prev = prevEdges[len(prevEdges) - 1]
            currentGraph = prev.toGraph
            tmpEdges = tgt_graph_dict[currentGraph].edges
            for tmpEdge in tmpEdges:
                cloneEdges = copy.deepcopy(prevEdges)
                cloneEdges.append(tmpEdge)
                list.append(cloneEdges)
        edgeSet = prevEdgeSet
        edgeSet[step] = list
    return edgeSet


def select_edge(src_idx_id_array, tgt_idx_id_array, tgt_graph_id, step, src_idx_id_array_start):
    matched_tgt_graph_idx = 'None'
    max = 0
    if src_idx_id_array_start < len(src_idx_id_array):
        src_idx_id_array_end = 0
        if len(src_idx_id_array) <= (src_idx_id_array_start+step):
            src_idx_id_array_end = len(src_idx_id_array)
        else:
            src_idx_id_array_end = src_idx_id_array_start+step
        candidate_edge = traverse(tgt_graph_id, step - 1, tar_dict)  # be careful step must greater than 1
        for step_n in candidate_edge:
            edges_n = candidate_edge[step_n]
            for candidate_tgt_edge_list in edges_n:
                tmp, record = similarity(candidate_tgt_edge_list, src_idx_id_array, src_idx_id_array_start, src_idx_id_array_end)
                if (tmp >= max):
                    max = tmp
                    if src_idx_id_array[src_idx_id_array_start]['activity'] in record:
                        matched_tgt_graph_idx = record[src_idx_id_array[src_idx_id_array_start]['activity']]
                    else:
                        matched_tgt_graph_idx = 'None'
    return matched_tgt_graph_idx, max


def convert(src_idx_array, tgt_idx_array, current_tgt_graph_id, step):
    res = []
    match_score = 0
    src_idx_array_start = 0
    while src_idx_array_start <= len(src_idx_array):
        edge, score = select_edge(src_idx_array, tgt_idx_array, current_tgt_graph_id, step, src_idx_array_start)
        if edge == 'None':
            break
        else:
            current_tgt_graph_id = edge.toGraph
            res.append(edge)
            match_score += score
            src_idx_array_start += 1
    return res, match_score


def graph_match_step_ver(src_idx_array, tgt_idx_array):
    step = 3
    max = 0
    res = []
    for tgt_id in tgt_idx_array:
        if tgt_id == 'com.ijoysoft.browser.activity.ActivityMain0':
            a=1
        match_info, match_score = convert(src_idx_array, tgt_idx_array, tgt_id, step)
        if match_score > max:
            max = match_score
            res = match_info
    return res


def similarity(candidate_tgt_edge_list, src_idx_id_array, src_idx_id_array_start, src_idx_id_array_end):
    res = 0
    record = {}
    probScore = 0
    match = []
    tmpRecord = {}
    if src_idx_id_array_start >= len(src_idx_id_array):
        res = 0
    elif len(candidate_tgt_edge_list) == 0:
        for i in range(src_idx_id_array_start, src_idx_id_array_end):
            res += MIN
            record.update({src_idx_id_array[i]['activity']: 'None'})
    else:
        tmp = 0
        tmpRes = 0
        currentMax = 0
        for i in range(src_idx_id_array_start, src_idx_id_array_end):
            last_edge = candidate_tgt_edge_list[len(candidate_tgt_edge_list) - 1]
            if src_idx_id_array_end > i:
                probScore, match = prob(last_edge, src_idx_id_array, i, src_idx_id_array_end)
            else:
                probScore, match = prob(last_edge, src_idx_id_array, len(src_idx_id_array), len(src_idx_id_array))
            new_end = i-1
            # subPrefix = []
            # if i==0:
            #     subPrefix = []
            # elif i==1:
            #     subPrefix = [src_idx_id_array[0]]
            # else:
            #     subPrefix = src_idx_id_array[0:i-1]
            if len(candidate_tgt_edge_list) == 1:
                tmpRes, tmpRecord = similarity([], src_idx_id_array, src_idx_id_array_start, new_end)
            else:
                tmpRes, tmpRecord = similarity(candidate_tgt_edge_list[0:len(candidate_tgt_edge_list) - 1], src_idx_id_array, src_idx_id_array_start, new_end)
            tmp = tmpRes + probScore
            if match:
                tmpRecord.update(match)
            if tmp>currentMax:
                currentMax = tmp
                record = tmpRecord
        if currentMax > res:
            res = currentMax
    return res, record


def prob(tgt_edge, src_graph_idx_id_list, src_list_start, src_list_end): #tgt graph, src graph
    res = 0
    match = {}
    tgt_prev_graph_id = tgt_edge.fromGraph
    tgt_next_graph_id = tgt_edge.toGraph
    tgt_node = tgt_edge.target
    if len(src_graph_idx_id_list) == src_list_start:
        res = 0
        match = {}
    else:
        tmp = 0
        for i in range(src_list_start, src_list_end-1):
            src_prev_graph_id = src_graph_idx_id_list[i]['activity']
            src_next_graph_id = src_graph_idx_id_list[i + 1]['activity']
            src_node = test_array[i]
            graph_sim = graph_sim_matrix[src_prev_graph_id+' '+tgt_prev_graph_id] + graph_sim_matrix[src_next_graph_id+' '+tgt_next_graph_id]
            elem_sim, elem_match = elemSim(tgt_node, src_node)
            tmp_value = graph_sim + elem_sim
            if tmp < tmp_value:
                tmp = tmp_value
                tmpEdge = Edge([elem_match], tgt_edge.event, tgt_edge.fromGraph, tgt_edge.toGraph)
                match = {src_prev_graph_id: tmpEdge}
        res += tmp
    # res += MIN * (len(refEdgeList) - 1) # that's the bug
    return res, match




def evt_sSim(path, idx_s, prev_src, tar_e, src_e, prev_tar, tar_idx):
    se = None if prev_src == -1 else src_e[prev_src]
    score = 0
    for p in path:
        if len(p) == 1:
            key = str(p[0])
            es = tar_e[key]
            if isinstance(es, list):
                for e in es:
                    v = elemSim(e, se)
                    score = v if v >= score else score
        else:
            for i in range(len(p) - 1):
                key = str(p[i]) + '' + str(p[i + 1])

                es = tar_e[key]
                if isinstance(es, list):
                    for e in es:
                        v = elemSim(e, se)
                        score = v if v >= score else score
    return score


def evt_sim(path, prev_src):
    """path is a set of edges from prev_tar to current_tar"""
    se = None if prev_src == -1 else test_array[prev_src]  # get src from test_array
    score = 0
    match_elem = None
    for i in range(len(path)):
        events = path[i].target
        for e in events:
            v = elemSim(e, se)
            if v >= score:
                score = v
                match_elem = e
                if isinstance(e, list):
                    match_elem[len(e) - 1]["activity"] = path[i].fromGraph
                else:
                    match_elem["activity"] = path[i].fromGraph
    return score, match_elem


def elemSim(e, se):
    max = 0
    match_ele = []
    if not se:
        return 0
    else:
        key = ''
        sid = se['id']
        stxt = se['text']
        scls = se['class']
        sdesc = se['content-desc']
        if isinstance(e, list):
            for elem in e:
                if isinstance(elem, list):
                    length = len(elem)
                    tid = elem[length-1]['resource-id'] if elem[length-1]['resource-id'].find("/") == -1 else elem[length-1]['resource-id'].split("/")[1]
                    ttxt = elem[length-1]['text']
                    tcls = elem[length-1]['class']
                    tdesc = elem[length-1]['content-desc']
                    tmp_key = str('tar' + tid + ' ' + elem[length-1]['index']) + "_" + str(se['id'] + "_list")
                else:
                    tid = elem['resource-id'] if elem['resource-id'].find("/") == -1 else elem['resource-id'].split("/")[1]
                    ttxt = elem['text']
                    tcls = elem['class']
                    tdesc = elem['content-desc']
                    tmp_key = str('tar' + tid + ' ' + elem['index']) + "_" + str(se['id'])

                if tmp_key in eSim:
                    v = eSim[tmp_key]
                else:
                    contentScore = arraySim(splitByUpper(ttxt), splitByUpper(stxt))
                    idScore = arraySim(splitByUpper(str(tid)), splitByUpper(str(sid)))
                    clsScore = arraySim(splitByUpper(str(tcls)), splitByUpper(str(scls)))
                    descScore = arraySim(splitByUpper(str(tdesc)), splitByUpper(str(sdesc)))
                    v = contentScore + idScore + clsScore + descScore
                    v /= 4
                    eSim.update({tmp_key: v})

                if max < v:
                    max = v
                    key = tmp_key
                    match_ele = elem
        # eSim.update({key: max})
    return max, match_ele



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



group = ['a31', 'a32', 'a33', 'a35']
srcFolder = ''
tarFolder = ''
cate = 'a3_b31'
for src in group:
    # if src != 'a35':
    #     continue
    srcFolder = src
    for tar in group:
        tarFolder = tar
        # if tar != 'a31':
        #     continue
        if src != tar:
            fileOBJ = open("data/" + cate + "/" + srcFolder + "_" + tarFolder + '_new.txt', 'w')

            pair = src + '_' + tar
            # pair = 'a31_a35'
            sim_json = "data/" + cate + "/sim_" + src + ".json"
            # sim_json = "data/sim_a31.json"
            src_json = "data/" + cate + "/src/" + src + "/activitiesSummary.json"
            # src_json = "data/src/a31/activitiesSummary.json"
            tar_json = "data/" + cate + "/tar/" + tar + "/activitiesSummary.json"
            # tar_json = "data/tar/a35/activitiesSummary.json"
            test_json = "data/" + cate + "/" + src + ".json"

            eSim = {}
            src_dict = Parser_me.parseJson2STG(src_json)
            tar_dict = Parser_me.parseJson2STG(tar_json)
            src_array = Parser_me.dict2array(src_dict)
            tar_array = Parser_me.dict2array(tar_dict)

            print(pair)

            graph_sim_matrix = Parser_me.parse_graph_json(sim_json)[pair]
            adjacent_matrix_tar = Parser_me.getAM(tar_dict)
            test_array = Parser_me.parse_test_file(test_json)

            res = graph_match_step_ver(test_array, tar_array)
            # print(len(res))
            # print(res[0].fromGraph, " ", res[0].toGraph, " ", res[0].target)
            # print('-------------------')
            for item in res:
                fileOBJ.write(item.fromGraph + '\n')
                fileOBJ.write(str(item.target[0]))
                fileOBJ.write('\n')
                fileOBJ.write(item.toGraph + '\n')
                fileOBJ.write('------------------------------------\n')

            fileOBJ.close()
            # GBTM()


