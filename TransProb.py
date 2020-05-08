from nltk.corpus import wordnet as wn
from itertools import product
import copy

MIN = -1


def sim(e1, e2):
    res = 0
    if True:
        content1 = e1.content
        content2 = e2.content
        id1 = e1.id
        id2 = e2.id
        contentScore = arraySim(splitByUpper(content1), splitByUpper(content2))
        idScore = arraySim(splitByUpper(str(id1)), splitByUpper(str(id2)))
        res = contentScore + idScore
    return res


def arraySim(strArray, strArray2):
    sum = 0
    for s1 in strArray:
        max = 0
        for s2 in strArray2:
            tmp = wordSim(s1, s2)
            max = max = tmp if tmp > max else max
        sum += max
    return sum


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


def traverse(graph, step):
    list = []
    edgeSet = {}
    if step == 1:
        for edge in graph.edges:
            tmp = []
            tmp.append(edge)
            list.append(tmp)
        edgeSet[step] = list
    else:
        prevEdgeSet = traverse(graph, step - 1)
        prevList = prevEdgeSet[step - 1]
        for i in prevList:
            prevEdges = i
            prev = prevEdges[len(prevEdges) - 1]
            currentGraph = prev.toGraph
            tmpEdges = currentGraph.edges
            for tmpEdge in tmpEdges:
                cloneEdges = copy.deepcopy(prevEdges)
                cloneEdges.append(tmpEdge)
                list.append(cloneEdges)
        edgeSet = prevEdgeSet
        edgeSet[step] = list
    return edgeSet


def selectEvent(reference, currentGraph, step):
    edge = []
    if len(reference) > 0:
        # the prefix can be length of 1 to step
        prefix = reference[0:step] # what if step>len(prefix)?
        candidate = traverse(currentGraph, step)
        max = 0
        for n in candidate:
            val = candidate[n]
            if n==2:
                a = 1
            for candidateList in val:
                tmp, record = similarity(candidateList, prefix, step)
                if (tmp >= max):
                    max = tmp
                    if str(reference[0].target.id) in record:
                        edge = record[str(reference[0].target.id)]
                    else:
                        edge = 'None'
    return edge


def findEdge(Edgelist):
    res = 'None'
    for e in Edgelist:
        if e != 'None':
            res = e
            break
    return res


def combine(target, array):
    for i in array:
        target.append(array)


def similarity(candidate, prefix, step):
    res = 0
    record = {}
    probScore = 0
    match = []
    tmpRecord = {}
    if len(prefix) == 0:
        res = 0
    elif len(candidate) == 0:
        for i in range(0, len(prefix)):
            res += MIN
            record.update({str(prefix[i].target.id): 'None'})
    else:
        tmp = 0
        tmpRes = 0
        currentMax = 0
        for i in range(0, step):
            if len(candidate)==3 and i==step-1:
                a=1
            last = candidate[len(candidate) - 1]
            if last.target.content == 'reader':
                a = 1
            if len(prefix) > i:
                probScore, match = prob(last, prefix[i:len(prefix)])
            else:
                probScore, match = prob(last, [])
            subPrefix = []
            if i==0:
                subPrefix = []
            elif i==1:
                subPrefix = [prefix[0]]
            else:
                subPrefix = prefix[0:i-1]
            if len(candidate) == 1:
                tmpRes, tmpRecord = similarity([], subPrefix, step)
            else:
                tmpRes, tmpRecord = similarity(candidate[0:len(candidate) - 1], subPrefix, step)
            tmp = tmpRes + probScore
            if match:
                tmpRecord.update(match)
            # combine(tmpRecord, match)
            if tmp>currentMax:
                currentMax = tmp
                record = tmpRecord
        if currentMax > res:
            res = currentMax
    return res, record


def prob(tarEdge, refEdgeList):
    res = 0
    match = {}

    if len(refEdgeList) == 0:
        res = 0
        match = {}
    else:
        tmp = 0
        for refEdge in refEdgeList:
            if refEdge:
                tmpRes = sim(tarEdge.target, refEdge.target)
                if tmp < tmpRes:
                    tmp = tmpRes
                    match = {str(refEdge.target.id): tarEdge}
        res += tmp
    # res += MIN * (len(refEdgeList) - 1) # that's the bug
    return res, match


def convert(targetEdgeList, currentGraph, step):
    res = []
    while len(targetEdgeList) > 0:
        edge = selectEvent(targetEdgeList, currentGraph, step) 
        if edge == 'None':
            break
        else:
            currentGraph = edge.toGraph
            res.append(edge)
            targetEdgeList = targetEdgeList[1:len(targetEdgeList)]
    return res


class Element:
    def __init__(self, id, type, content):
        self.id = id
        self.type = type
        self.content = content


class Edge:
    def __init__(self, target, event, fromGraph, toGraph):
        self.target = target
        self.event = event
        self.fromGraph = fromGraph
        self.toGraph = toGraph


class Graph:
    def __init__(self, id):
        self.id = id
        self.edges = []


def test():
    e1 = Element(1, 'btn', 'reader')
    e2 = Element(2, 'btn', 'my likes')
    e3 = Element(3, 'btn', 'menu')
    e4 = Element(4, 'item', 'share')

    te1 = Element(1, 'btn', 'notification')
    te2 = Element(2, 'btn', 'reader')
    te3 = Element(3, 'btn', 'my like')
    te4 = Element(4, 'list', 'discover')
    te5 = Element(5, 'btn', 'likes')
    te6 = Element(6, 'btn', 'ctx_menu')
    te7 = Element(7, 'btn', 'share')
    te8 = Element(8, 'btn', 'discover')

    g1 = Graph(1)
    g2 = Graph(2)
    g3 = Graph(3)
    g4 = Graph(4)
    g5 = Graph(5)

    tg1 = Graph(1)
    tg2 = Graph(2)
    tg3 = Graph(3)
    tg4 = Graph(4)
    tg5 = Graph(5)
    tg6 = Graph(6)
    tg7 = Graph(7)
    tg8 = Graph(8)
    tg9 = Graph(9)

    edge1 = Edge(e1, 'click', g1, g2)
    edge2 = Edge(e2, 'click', g2, g3)
    edge3 = Edge(e3, 'click', g3, g4)
    edge4 = Edge(e4, 'click', g4, g5)
    g1.edges.append(edge1)
    g2.edges.append(edge2)
    g3.edges.append(edge3)
    g4.edges.append(edge4)

    teg1 = Edge(te1, 'click', tg1, tg2)
    teg2 = Edge(te2, 'click', tg1, tg3)
    teg3 = Edge(te3, 'click', tg3, tg4)
    teg4 = Edge(te4, 'click', tg3, tg5)
    teg5 = Edge(te5, 'click', tg5, tg6)
    teg6 = Edge(te6, 'click', tg6, tg7)
    teg7 = Edge(te7, 'click', tg7, tg8)
    teg8 = Edge(te8, 'click', tg4, tg9)
    tg1.edges.append(teg1)
    tg1.edges.append(teg2)
    tg3.edges.append(teg3)
    tg3.edges.append(teg4)
    tg4.edges.append(teg8)
    tg5.edges.append(teg5)
    tg6.edges.append(teg6)
    tg7.edges.append(teg7)

    minTmp = sim(e1, te1)
    pair = {}
    for e in [e1, e2, e3, e4]:
        for te in [te1, te2, te3, te4, te5, te6, te7]:
            v = sim(e, te)
            if v < minTmp:
                minTmp = v
                pair = {e.content: te.content}
    global  MIN
    MIN = minTmp
    targetEdgeList = [edge1, edge2, edge3, edge4]
    currentGraph = tg1
    res, ways = connect(tg1,tg8,{})
    for way in ways:
        for e in way:
            print(e.target.id)
    # res = convert(targetEdgeList, currentGraph, 3)
    # for i in res:
    #     print(i.target.content)



def connect(graph, target, visitedGraph):
    flag = False
    way = []
    visitedGraph[graph.id] = True
    edges = graph.edges
    graphs = []
    for e in edges:
        if e.toGraph.id == target.id:
            flag = True
            path = [e]
            way.append(path)
        graphs.append(e.toGraph)
    if not flag:
        for e in edges:
            g = e.toGraph
            if g.id not in visitedGraph:
                visitedGraph[g.id] = True
                tmp, ways = connect(g, target, visitedGraph)
                if tmp:
                    flag = tmp
                    for tmpPath in ways:
                        if tmpPath:
                            newPath = [e]
                            newPath.extend(tmpPath)
                            way.append(newPath)
    return flag, way



test()