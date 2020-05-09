import json
import re
import Parser_me
import copy

def score_count(app_cate, task, srcFolder, tarFolder, suffix):
    precisionAvg = 0
    recallAvg = 0
    count = 0
    cate = app_cate + "_" + task
    # 'a51', 'a52', 'a53', 'a54', 'a55'
    for src in srcFolder:
        for tar in tarFolder:
            if src == tar:
                continue
            dataPath = "data/" + cate + "/"
            resPath = "data/" + cate + "/"
            resFile = resPath + src + "_" + tar + suffix + ".txt"
            srcTestFile = dataPath + src + ".json"
            tarTestFile = dataPath + tar + ".json"
            groundTruthFile = "groundtruth/" + app_cate + "/" + task + "/" + src + "-" + tar + "-" + task + ".json"

            tar_json = "data/" + cate + "/tar/" + tar + "/activitiesSummary.json"
            tar_dict = Parser_me.parseJson2STG(tar_json)
            tar_array = Parser_me.dict2array(tar_dict)
            adjacent_matrix_tar = Parser_me.getAM(tar_dict)

            srcTestArray = readJson(srcTestFile)
            tarTestArray = readJson(tarTestFile)
            groundTruthArray = readJson(groundTruthFile)
            generatedArray = []
            generatedActivityArray = []

            matchCount = -1
            existCount = -1
            matchTotal = len(groundTruthArray)
            generatedTotal = -1

            with open(resFile, encoding="utf-8") as f:
                lines = f.readlines()

            # generated act: act1 - event1 - act2 -...- event(N-1) - act N
            idx = 1
            for i in range(matchTotal + 1):  # -1, last oracle
                generatedArray.append(lines[idx])
                idx += 1
                generatedActivityArray.append(lines[idx].replace('\n', ''))
                idx += 1
                idx += 1

            generatedEventArray = {}
            idx = -1
            for item in generatedArray:
                item = stringTojson(item)
                if str(idx) in item:
                    generatedEventArray[idx] = item[str(idx)]
                else:
                    generatedEventArray[idx] = {"resource-id": "none", "class": "none", "content-desc": "none",
                                                "type": "empty"}
                idx += 1
            tmpGeneratedEventArray = copy.deepcopy(generatedEventArray)
            generatedEventArray = []
            for i in range(len(generatedActivityArray)):
                if i == 0:
                    continue
                prev = generatedActivityArray[i - 1]
                curr = generatedActivityArray[i]
                if prev == curr or tmpGeneratedEventArray[i - 1]["type"] == "back":
                    generatedEventArray.append(tmpGeneratedEventArray[i - 1])
                else:
                    elemID = tmpGeneratedEventArray[i - 1]["resource-id"]
                    elemClass = tmpGeneratedEventArray[i - 1]["class"]
                    elemDesc = tmpGeneratedEventArray[i - 1]["content-desc"]
                    elemType = tmpGeneratedEventArray[i - 1]["type"]
                    connect, path = getPath(tar_array.index(prev), tar_array.index(curr), adjacent_matrix_tar, [],tar_dict,tar_array)
                    if connect or prev == curr:
                        for p in path:
                            isMatch = False
                            step_tar = len(p)
                            if step_tar >= 3:
                                continue
                            tmpEvt = []
                            for edge in p:
                                evt = edge.target
                                for elem in evt:
                                    tmpEvt.append(elem)
                                    if isinstance(elem, list):
                                        for item in elem:
                                            if item["resource-id"] == elemID and item["class"] == elemClass and item[
                                                "content-desc"] == elemDesc:
                                                isMatch = True
                                    elif elem["type"] == "back":
                                        if elemType == "back":
                                            isMatch = True

                                    elif elem["resource-id"] == elemID and elem["class"] == elemClass and elem[
                                        "content-desc"] == elemDesc:
                                        isMatch = True
                            if isMatch:
                                generatedEventArray.extend(tmpEvt)
                                break
            length = len(generatedEventArray)
            i = -1
            while (1):
                # for i in range(len(generatedEventArray)):
                i += 1
                if (i == len(generatedEventArray)):
                    break
                item = copy.deepcopy(generatedEventArray[i])
                if isinstance(item, str):
                    continue
                if not isinstance(item, list):
                    if item["type"] == "back":
                        generatedEventArray[i] = "BACK"
                        continue
                    id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[
                        1]
                    generatedEventArray[i] = id + "->" + item["class"] + "->" + item["content-desc"]
                    continue
                # operation i is a list
                tmpItem = item[len(item) - 1]
                id = tmpItem["resource-id"] if tmpItem["resource-id"].find("/") == -1 else \
                tmpItem["resource-id"].split("/")[1]
                generatedEventArray[i] = id + "->" + tmpItem["class"] + "->" + tmpItem["content-desc"]
                for elem in item:
                    id = elem["resource-id"] if elem["resource-id"].find("/") == -1 else elem["resource-id"].split("/")[
                        1]
                    elemkey = id + "->" + elem["class"] + "->" + elem["content-desc"]
                    if elemkey not in generatedEventArray:
                        generatedEventArray.insert(i, elemkey)
            matchEventArray = []
            for key in tmpGeneratedEventArray:
                if key != -1:
                    item = tmpGeneratedEventArray[key]
                    if item["type"] == "back":
                        id = "BACK"
                        matchEventArray.append(id)
                        continue

                    id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[
                        1]
                    matchEventArray.append(id + "->" + item["class"] + "->" + item["content-desc"])

            # generatedEventArray [id-cls-desc, id-cls-desc]  all operation
            # matchEventArray     [id-cls-desc, id-cls-desc]  corresponding operation

            for i in range(len(groundTruthArray)):
                item = groundTruthArray[i]
                if groundTruthArray[i]["event_type"] == "SYS_EVENT":
                    groundTruthArray[i] = "BACK"
                elif groundTruthArray[i]["event_type"] == "stepping":
                    groundTruthArray[i] = "ANY"
                else:
                    id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[
                        1]
                    groundTruthArray[i] = id + "->" + item["class"] + "->" + item["content-desc"]

            TP = 0
            FP = 0
            FN = 0

            for i in range(len(groundTruthArray)):
                if groundTruthArray[i] == "ANY" or groundTruthArray[i] == matchEventArray[i]:
                    TP += 1
                if groundTruthArray[i] != "ANY" and groundTruthArray[i] not in generatedEventArray:
                    FN += 1

            FP = len(groundTruthArray) - TP

            precision = TP / (TP + FP)
            if TP + FN == 0:
                recall = 0
            else:
                recall = TP / (TP + FN)

            precisionAvg += precision
            recallAvg += recall
            count+=1
            print(src,'_', tar, "precision: ", precision, ", recall: ", recall)

    print("P: ", precisionAvg / count, ", R: ",
          recallAvg / count)


def get_edge(from_graph_idx, to_graph_idx, tar_dict, tar_array):
    edge = None
    edges = tar_dict[tar_array[from_graph_idx]].edges
    for e in edges:
        if e.toGraph == tar_array[to_graph_idx]:
            edge = e
            break
    return edge

def getPath(fromGraph, toGraph, am, visited, tar_dict, tar_array):
    if fromGraph == -1:
        return True, []
    visited.append(fromGraph)
    connect = am[fromGraph][toGraph] == 1
    way = []
    if connect:
        way.append([get_edge(fromGraph, toGraph, tar_dict, tar_array)])
    for i in range(len(am)):
        if am[fromGraph][i] == 1 and i not in visited:
            tmp, ways = getPath(i, toGraph, am, visited, tar_dict, tar_array)
            if tmp:
                connect = tmp
                for tmpPath in ways:
                    if tmpPath:
                        newPath = [get_edge(fromGraph, i, tar_dict, tar_array)]
                        newPath.extend(tmpPath)
                        way.append(newPath)
    return connect, way

def readJson(filename):
    with open(filename) as f:
        content = json.load(f)
    return content

def stringTojson(str):
    res = {}
    str = str.replace('\'', '\"').replace('None', '{\"None\"}')
    str = re.split('{|}', str)

    # print(str)

    idx = 0
    while idx < len(str):
        val = str[idx]
        if val == '' or val == '\n':
            idx += 1
            continue
        if idx % 2 == 1:
            key = val.replace(',', '').replace(':', '').replace(' ', '')
        idx += 1
        val = str[idx]
        if str[idx] != '"None"':
            val = "{" + str[idx] + "}"
            val = json.loads(val)

        res[key] = val
        idx += 1

    return res

# precisionAvg = 0
# recallAvg = 0
# cate1 = "a4"
# cate2 = "b41"
# cate = cate1 + "_" + cate2 #+"_tmp"
# # 'a51', 'a52', 'a53', 'a54', 'a55'
# srcFolder = ['a41', 'a42', 'a43', 'a44', 'a45']
# tarFolder = ['a41', 'a42', 'a43', 'a44', 'a45']
# for src in srcFolder:
#     for tar in tarFolder:
#         if src == tar:
#             continue
#         # src = "a33"
#         # tar = "a32"
#         print(src, " ", tar, " ", cate)
#
#         dataPath = "data/" + cate + "/"
#         resPath = "data/" + cate + "/"
#         resFile = resPath + src + "_" + tar + "_T.txt"
#         srcTestFile = dataPath + src + ".json"
#         tarTestFile = dataPath + tar + ".json"
#         groundTruthFile = "groundtruth/" + cate1 + "/" + cate2 + "/" + src + "-" + tar + "-" + cate2 + ".json"
#
#         tar_json = "data/" + cate + "/tar/" + tar + "/activitiesSummary.json"
#         tar_dict = Parser.parseJson2STG(tar_json)
#         tar_array = Parser.dict2array(tar_dict)
#         adjacent_matrix_tar = Parser.getAM(tar_dict)
#
#         srcTestArray = readJson(srcTestFile)
#         tarTestArray = readJson(tarTestFile)
#         groundTruthArray = readJson(groundTruthFile)
#         generatedArray = []
#         generatedActivityArray = []
#
#         matchCount = -1
#         existCount = -1
#         matchTotal = len(groundTruthArray)
#         generatedTotal = -1
#
#
#         with open(resFile, encoding="utf-8") as f:
#             lines = f.readlines()
#
#         # generated act: act1 - event1 - act2 -...- event(N-1) - act N
#         idx = 1
#         for i in range(matchTotal + 1):  # -1, last oracle
#             generatedArray.append(lines[idx])
#             idx += 1
#             generatedActivityArray.append(lines[idx].replace('\n', ''))
#             idx += 1
#             idx += 1
#
#         generatedEventArray = {}
#         idx = -1
#         for item in generatedArray:
#             item = stringTojson(item)
#             if str(idx) in item:
#                 generatedEventArray[idx] = item[str(idx)]
#             else:
#                 generatedEventArray[idx] = {"resource-id":"none", "class":"none", "content-desc":"none", "type":"empty"}
#             idx += 1
#
#
#         # connect, path = getPath(prev_tar_idx, i, adjacent_matrix_tar, [])
#         # if connect or i == prev_tar_idx:
#
#
#         tmpGeneratedEventArray = copy.deepcopy(generatedEventArray)
#         generatedEventArray = []
#
#         for i in range(len(generatedActivityArray)):
#             if i == 0:
#                 continue
#             prev = generatedActivityArray[i-1]
#             curr = generatedActivityArray[i]
#             if prev == curr or tmpGeneratedEventArray[i-1]["type"] == "back":
#                 generatedEventArray.append(tmpGeneratedEventArray[i-1])
#             else:
#                 elemID = tmpGeneratedEventArray[i-1]["resource-id"]
#                 elemClass = tmpGeneratedEventArray[i-1]["class"]
#                 elemDesc = tmpGeneratedEventArray[i-1]["content-desc"]
#                 elemType = tmpGeneratedEventArray[i-1]["type"]
#                 connect, path = getPath(tar_array.index(prev), tar_array.index(curr), adjacent_matrix_tar, [])
#                 if connect or prev == curr:
#                     for p in path:
#                         isMatch = False
#                         step_tar = len(p)
#                         if step_tar >= 3:
#                             continue
#                         tmpEvt = []
#                         for edge in p:
#                             evt = edge.target
#                             for elem in evt:
#                                 tmpEvt.append(elem)
#                                 if isinstance(elem, list):
#                                     for item in elem:
#                                         if item["resource-id"] == elemID and item["class"] == elemClass and item["content-desc"] == elemDesc:
#                                             isMatch = True
#                                 elif elem["type"] == "back":
#                                     if elemType == "back":
#                                         isMatch = True
#
#                                 elif elem["resource-id"] == elemID and elem["class"] == elemClass and elem["content-desc"] == elemDesc:
#                                     isMatch = True
#                         if isMatch:
#                             generatedEventArray.extend(tmpEvt)
#                             break
#
#         length = len(generatedEventArray)
#         i = -1
#         while(1):
#         # for i in range(len(generatedEventArray)):
#             i += 1
#             if (i == len(generatedEventArray)):
#                 break
#             item = copy.deepcopy(generatedEventArray[i])
#             if isinstance(item, str):
#                 continue
#             if not isinstance(item, list):
#                 if item["type"] == "back":
#                     generatedEventArray[i] = "BACK"
#                     continue
#                 id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[1]
#                 generatedEventArray[i] = id + "->" + item["class"] + "->" + item["content-desc"]
#                 continue
#
#             # operation i is a list
#             tmpItem = item[len(item) - 1]
#             id = tmpItem["resource-id"] if tmpItem["resource-id"].find("/") == -1 else tmpItem["resource-id"].split("/")[1]
#             generatedEventArray[i] = id + "->" + tmpItem["class"] + "->" + tmpItem["content-desc"]
#             for elem in item:
#                 id = elem["resource-id"] if elem["resource-id"].find("/") == -1 else elem["resource-id"].split("/")[1]
#                 elemkey = id + "->" + elem["class"] + "->" + elem["content-desc"]
#                 if elemkey not in generatedEventArray:
#                     generatedEventArray.insert(i, elemkey)
#
#
#         matchEventArray = []
#         for key in tmpGeneratedEventArray:
#             if key != -1:
#                 item = tmpGeneratedEventArray[key]
#                 if item["type"] == "back":
#                     id = "BACK"
#                     matchEventArray.append(id)
#                     continue
#
#                 id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[1]
#                 matchEventArray.append(id + "->" + item["class"] + "->" + item["content-desc"])
#
#         # generatedEventArray [id-cls-desc, id-cls-desc]  all operation
#         # matchEventArray     [id-cls-desc, id-cls-desc]  corresponding operation
#
#         for i in range(len(groundTruthArray)):
#             item = groundTruthArray[i]
#             if groundTruthArray[i]["event_type"] == "SYS_EVENT":
#                 groundTruthArray[i] = "BACK"
#             elif groundTruthArray[i]["event_type"] == "stepping":
#                 groundTruthArray[i] = "ANY"
#             else:
#                 id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[1]
#                 groundTruthArray[i] = id + "->" + item["class"] + "->" + item["content-desc"]
#
#
#         TP = 0
#         FP = 0
#         FN = 0
#
#         for i in range(len(groundTruthArray)):
#             if groundTruthArray[i] == "ANY" or groundTruthArray[i] == matchEventArray[i]:
#                 TP += 1
#             if groundTruthArray[i] != "ANY" and groundTruthArray[i] not in generatedEventArray:
#                 FN += 1
#
#         FP = len(groundTruthArray) - TP
#
#         precision = TP / (TP + FP)
#         if TP + FN == 0:
#             recall = 0
#         else:
#             recall = TP / (TP + FN)
#
#
#         precisionAvg += precision
#         recallAvg += recall
#         print("precision: ", precision, ", recall: ", recall)
#
# print("P: ", precisionAvg / len(srcFolder) / (len(tarFolder) - 1), ", R: ", recallAvg / len(srcFolder) / (len(tarFolder) - 1))









# print(lines[2])