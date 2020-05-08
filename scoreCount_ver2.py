import json
import re
import Parser_me
import copy

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

def readJson(filename):
    with open(filename) as f:
        content = json.load(f)
    return content

def stringTojson(str):
    res = {}
    str = str.replace('\'', '\"').replace('None', '{\"None\"}').replace(' -1', ' {\"None\"}')
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
        if str[idx] != '"None"' and str[idx] != '-1':
            val = "{" + str[idx] + "}"
            val = json.loads(val)

        res[key] = val
        idx += 1

    return res

precisionAvg = 0
recallAvg = 0
cate1 = "a1"
cate2 = "b12"
cate = cate1 + "_" + cate2
# 'a51', 'a52', 'a53', 'a54', 'a55'
srcFolder = ['a11', 'a12', 'a13', 'a14', 'a15']
tarFolder = ['a11', 'a12', 'a13', 'a14', 'a15']
for src in srcFolder:
    for tar in tarFolder:
        if src == tar:
            continue
        # src = "a33"
        # tar = "a32"
        print(src, " ", tar, " ", cate)

        dataPath = "data/" + cate + "/"
        resFile = dataPath + 'res/' + src + "_" + tar + "_Step2.txt"
        pathFile = dataPath + 'res/' + src + "_" + tar + "_Step2.json"
        srcTestFile = dataPath + src + ".json"
        tarTestFile = dataPath + tar + ".json"
        groundTruthFile = "groundtruth/" + cate1 + "/" + cate2 + "/" + src + "-" + tar + "-" + cate2 + ".json"

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

        idx = 1
        while 1:
            if "time" not in lines[idx]:
                generatedArray.append(lines[idx])
                idx += 1 # for act
                idx += 1 # for '---'
                idx += 1 # maybe arr or time
            else:
                break

        generatedEventArray = {}
        idx = -1
        for item in generatedArray:
            item = stringTojson(item)
            for key in item:
                if "None" in item[key]:
                    generatedEventArray[int(key)] = {"resource-id":"none", "class":"none", "content-desc":"none", "type":"empty"}
                else:
                    generatedEventArray[int(key)] = item[key]

        matchEventArray = []
        for key in generatedEventArray:
            if key != -1:
                item = generatedEventArray[key]
                if "type" in item and item["type"] == "back":
                    id = "BACK"
                    matchEventArray.append(id)
                    continue

                id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[1]
                matchEventArray.append(id + "->" + item["class"] + "->" + item["content-desc"])

        tmpGeneratedEventArray = readJson(pathFile)
        generatedEventArray = []
        for edge in tmpGeneratedEventArray:
            if isinstance(edge, dict):
                items = edge["target"]
                if isinstance(items, list):
                    items = items[0]
                if isinstance(items, list):
                    for item in items:
                        eID = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[1]
                        elemkey = eID + "->" + item["class"] + "->" + item["content-desc"]
                        if elemkey not in generatedEventArray:
                            generatedEventArray.append(elemkey)
                else:
                    item = items
                    if "type" in item and item["type"] == "back":
                        eID = "BACK"
                        generatedEventArray.append(eID)
                        continue
                    eID = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[1]
                    elemkey = eID + "->" + item["class"] + "->" + item["content-desc"]
                    generatedEventArray.append(elemkey)


        # generatedEventArray [id-cls-desc, id-cls-desc]  all operation
        # matchEventArray     [id-cls-desc, id-cls-desc]  corresponding operation
        a = 1
        for i in range(len(groundTruthArray)):
            item = groundTruthArray[i]
            if groundTruthArray[i]["event_type"] == "SYS_EVENT":
                groundTruthArray[i] = "BACK"
            elif groundTruthArray[i]["event_type"] == "stepping":
                groundTruthArray[i] = "ANY"
            else:
                id = item["resource-id"] if item["resource-id"].find("/") == -1 else item["resource-id"].split("/")[1]
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
        print("precision: ", precision, ", recall: ", recall)

print("P: ", precisionAvg / len(srcFolder) / (len(tarFolder) - 1), ", R: ", recallAvg / len(srcFolder) / (len(tarFolder) - 1))
