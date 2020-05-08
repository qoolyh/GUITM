import math
from nltk.corpus import wordnet as wn
from itertools import product
import Parser_me
import time
import simCal
import copy

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
    return sum/len(strArray)


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
    fileOBJ = open("data/" + cate + "/" + srcFolder + "_" + tarFolder + '11111.txt', 'w')
    start_time = time.time()
    tarIndex = -1
    res = {}
    print("start " + srcFolder + "_" + tarFolder)
    fileOBJ.write("start\n")
    for i in range(len(test_array)):
        # if i == 6:
        #     print("step in")
        if i == 1:
            a = 1
        score, tmpRes, ind = GraphMatch(i-1, tarIndex, i, 0, {})
        tarIndex = ind
        print(tarIndex)
        print(tar_array[tarIndex])
        print(tmpRes)
        fileOBJ.write(str(tmpRes) + "\n")
        # print(tar_array[tarIndex])
        fileOBJ.write(tar_array[tarIndex] + "\n")
        fileOBJ.write("--------------------------------------------------------" + "\n")
        if i-1 in tmpRes:
            haveMatched[i-1] = tmpRes[i-1]
            res[i-1] = tmpRes[i-1]
    end_time = time.time()
    # print('----time:', (end_time-start_time))
    fileOBJ.write('----time:' + str(end_time-start_time) + "\n")

    for k in res:
        if res[k]:
            if isinstance(res[k], list):
                # print("list", " ", test_array[k]['text'], " ", test_array[k]['content-desc'], '.......', k, '.......',
                #       res[k][len(res[k])-1]['text'], " ", res[k][len(res[k])-1]['content-desc'], " ", res[k][len(res[k])-1]['activity'])
                fileOBJ.write("list" + " " + test_array[k]['text'] + " " + test_array[k]['content-desc'] + '.......' + str(k) + '.......' +
                      res[k][len(res[k])-1]['text'] + " " + res[k][len(res[k])-1]['content-desc'] + " " + res[k][len(res[k])-1]['activity'] + "\n")
            elif not isinstance(res[k], int) and res[k]["type"] == "back":
                fileOBJ.write("BACK_EVENT ......\n")
            elif not isinstance(res[k], int):
                # print(str(test_array[k]['text']), " ", str(test_array[k]['content-desc']), '.......', str(k), '.......',
                #       str(res[k]['text']), " ", str(res[k]['content-desc']), " ", str(res[k]['activity']))
                fileOBJ.write(str(test_array[k]['text']) + " " + str(test_array[k]['content-desc']) + '.......' + str(k) + '.......' +
                      str(res[k]['text']) + " " + str(res[k]['content-desc']) + " " + str(res[k]['activity']) + "\n")
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


# def oracle_handler(elem):
#     type = elem.action[0]
#     if type == 'wait_until_element_presence':
#         expect =


def GraphMatch(prev_src, prev_tar, curr_src, steps, matched):
    match = -1
    score = 0
    match_info = {}
    resTarIndex = -1

    if steps == 3:
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
            # if i == 17:
            #     print("1")
            # graph_sim = graph_sim_matrix[curr_src_graph + ' ' + tar_array[i]]
            graph_sim = calculateGraphSim(curr_src, tar_array[i])

            # if graph_sim <= 0.2:
            #     continue
            # if tar_array[i] == "com.yelp.android.ui.activities.ActivityCreateAccount0" or tar_array[i] == "com.yelp.android.ui.activities.collections.ActivityCollectionsViewV20":
            #     if curr_src == 0:
            #         print(1)
            # else:
            #     continue
            next_score, next_match, _ = GraphMatch(curr_src, i, curr_src + 1, steps + 1, copy.deepcopy(matched))
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
            prev_src_graph = test_array[prev_src-1]['activity']
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
                            tmp_score = graph_sim / step_cost + elemSim(tar_elem, src_elem, matched, tar_edge.fromGraph)
                            if matching_score <= tmp_score:
                                matching_score = tmp_score
                                e_match = tar_elem
                                if isinstance(tar_elem, list):
                                    e_match[len(tar_elem)-1]["activity"] = tar_edge.fromGraph
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
                        e_sim, tar_match = evt_sim(p, prev_src, matched)
                        tmp_score = graph_sim / step_cost + e_sim
                        if tmp_score >= matching_score:
                            matching_score = tmp_score
                            e_match = tar_match

            # matched改成prev和cur为键
            if e_match == -1:
                continue
            new_matched = updateMatched(copy.deepcopy(e_match), copy.deepcopy(matched))
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

def updateMatched(matchEles, matchedSet):
    if isinstance(matchEles, list):
        matchEles = matchEles[len(matchEles) - 1]
    elif not isinstance(matchEles, dict) or matchEles == {}:
        return matchedSet

    ele = matchEles
    if isinstance(ele, list):
        ele = ele[len(ele)-1]
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

# 0-A, 1-B, 2-C    A-a-B B-b-C C-c-D
#match: 0-A
# 1 b, b->n
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
        if e[length-1]['resource-id'].find("/") != -1:
            tid = e[length-1]['resource-id'].split("/")[1]
        else:
            tid = e[length-1]['resource-id']
        key = str('tar' + tid + ' ' + e[length-1]['index']) + "_" + str(se['id'] + "_list")
    else:
        if e['resource-id'].find("/") != -1:
            tid = e['resource-id'].split("/")[1]
        else:
            tid = e['resource-id']
        key = str('tar' + tid + ' ' + e['index']) + "_" + str(se['id'])

    sid = se['id']
    # if tid == "email_sign_up" and sid == "login_fragment_create_account_button":
    #     a = 1
    # if tid == "create" and sid == "login_fragment_create_account_button":
    #     a = 1
    # if tid == "toolbar_search_text" and sid == "login_fragment_create_account_button":
    #     a = 1
    # if key == "tarcreate_account_fragment_first_name_text 0_create_account_fragment_password_text"\
    #     or key == "tarcreate_account_fragment_last_name_text 1_create_account_fragment_password_text"\
    #     or key == "tarbug_report 2_create_account_fragment_email_text":
    #     print("take care")
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
        v = contentScore + idScore + clsScore + descScore
        v/=4

        eSim.update({key: v})

    return v


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
    test_node = test_array[test_idx]
    if 'activity' not in test_node:
        test_node = test_array[test_idx - 1]
    src_activity = test_node['activity']
    src_graph_elems = src_dict[src_activity].elements
    tar_graph_elems = tar_dict[tar_id].elements
    key = str(test_idx) + "_" + str(tar_id)
    if key in cache:
        return cache[key]
    toDeleteElem = {"id": test_node["resource-id"], "class": test_node["class"]}
    src_graph_elems = deleteElem(src_graph_elems, toDeleteElem)
    v = simCal.graphSim_TFIDF(src_graph_elems, tar_graph_elems)
    cache[key] = v
    return v


def deleteElem(graph, elem):
    graph = copy.deepcopy(graph)
    elemId = elem["id"]
    for idx in range(len(graph)):
        eID = graph[idx].id[0]
        if eID == elemId:
            graph.pop(idx)
            break
    return graph

graphSim = [[0.3184, 0.1477, 0.1755, 0.1761],
            [0.2091, 0.1506, 0.1752, 0.208],
            [0.217, 0.1662, 0.1727, 0.2422],
            [0.2123, 0.1926, 0.2291, 0.1879],
            [0.2258, 0.2743, 0.2649, 0.2371],
            [0.2338, 0.2195, 0.2428, 0.2232],
            ]
group = ['a31', 'a32', 'a33', 'a35']
srcFolder = ''
tarFolder = ''
cate = 'a3_b31'
haveMatched = {}
for src in group:
    if src != 'a33':
        continue
    srcFolder = src
    for tar in group:
        tarFolder = tar
        if tar != 'a32':
            continue
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

            eSim = {}
            src_dict = Parser_me.parseJson2STG(src_json)
            tar_dict = Parser_me.parseJson2STG(tar_json)
            src_array = Parser_me.dict2array(src_dict)
            tar_array = Parser_me.dict2array(tar_dict)

            graph_sim_matrix = Parser_me.parse_graph_json(sim_json)[pair]
            adjacent_matrix_tar = Parser_me.getAM(tar_dict)
            test_array = Parser_me.parse_test_file(test_json)
            GBTM()


