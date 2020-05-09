from nltk.corpus import wordnet as wn
from itertools import product
import copy
import ElemSim
import numpy
MIN = -1

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
    def __init__(self, id, elems):
        self.id = id
        self.edges = []
        self.elements = elems

# def GBMT(test, targetGraphSet):
#     sourceGraph = []
#     matchedGraph = []
#     synthesizedTest = []
#     previous = None
#     sourceGraphSet = getGraph(test)
#     matchedGraph = graphMatch(sourceGraphSet, targetGraphSet, None, 0)
#     for t in test:
#         graph = getGraph(t)
#         sourceGraph.append(graph)
#         bestMatch = graphMatch(sourceGraph, targetGraphSet, previous)
#         previous = bestMatch
#         matchedGraph.append(bestMatch)
#     for i in range[0,len(matchedGraph)-1]:
#         current = matchedGraph[i]
#         next = matchedGraph[i+1]
#         path = findPath(current, next, None)
#         matchedElement, idx = elemMatch(test[i], path, current)
#         newTest = generateTest(matchedElement, test[i], idx, path)
#         synthesizedTest.append(newTest)
#     return synthesizedTest


def getAM(graphSet):
    am = numpy.zeros((len(graphSet),len(graphSet)))
    for i in range(0, len(graphSet)):
        edges = graphSet[i].edges
        for e in edges:
            toGraph = e.toGraph
            am[i][graphSet.index(toGraph)] = 1
    return am


def getPath(fromGraph, toGraph, am, visited):
    visited.append(fromGraph)
    connect = am[fromGraph][toGraph]==1
    way = []
    if connect:
        path = [fromGraph]
        way.append(path)
    for i in range(len(am)):
        if am[fromGraph][i] == 1 and i not in visited:
            tmp, ways = getPath(i, toGraph, am, visited)
            if tmp:
                connect = tmp
                for tmpPath in ways:
                    if tmpPath:
                        newPath = [fromGraph]
                        newPath.extend(tmpPath)
                        way.append(newPath)
    return connect, way


def connected(idx1, idx2, am, visited):
    visited.append(idx1)
    connect = am[idx1][idx2]==1 or idx1 == -1
    if connect:
        return True
    else:
        for i in range(len(am)):
            if am[idx1][i] == 1 and i not in visited:
                tmp = connected(i, idx2, am, visited)
                if tmp:
                    return True
    return connect


def graphMatch(sourceSet, targetSet, previous, idx, adjacentMatrix):
    score = 0
    if idx == len(sourceSet):
        return score, {}
    match = -1
    res = {}
    tmpRes = {}
    for tg in range(len(targetSet)):
        if connected(previous, tg, adjacentMatrix,[]):
            tmpScore, mch = graphMatch(sourceSet, targetSet, tg, idx+1, adjacentMatrix)
            matchingScore = graphSim_test(sourceSet[idx],targetSet[tg]) + tmpScore
            if score <= matchingScore:
                score = matchingScore
                match = tg
                tmpRes = mch
    tmp = {idx:match}
    tmp.update(tmpRes)
    return score, tmp


def graphSim_test(g1, g2):
    score = 0
    E1 = g1.elements
    E2 = g2.elements
    for elem1 in E1:
        max = 0
        for elem2 in E2:
            v = ElemSim.sim(elem1,elem2)
            max = max if max > v else v
        score+=max
    score /= len(E1)
    return score


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

    g1 = Graph(1,[e1])
    g2 = Graph(2,[e2])
    g3 = Graph(3,[e3])
    g4 = Graph(4,[e4])
    g5 = Graph(5,[])

    tg1 = Graph(1,[te1,te2])
    tg2 = Graph(2,[])
    tg3 = Graph(3,[te3,te4,te1])
    tg4 = Graph(4,[te8])
    tg5 = Graph(5,[te5])
    tg6 = Graph(6,[te6])
    tg7 = Graph(7,[te7])
    tg8 = Graph(8,[])
    tg9 = Graph(9,[])

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
    teg9 = Edge(te1, 'click', tg3, tg8)
    teg8 = Edge(te8, 'click', tg4, tg9)
    tg1.edges.append(teg1)
    tg1.edges.append(teg2)
    tg3.edges.append(teg3)
    tg3.edges.append(teg4)
    tg3.edges.append(teg9)
    tg4.edges.append(teg8)
    tg5.edges.append(teg5)
    tg6.edges.append(teg6)
    tg7.edges.append(teg7)


    minTmp = ElemSim.sim(e1, te1)
    pair = {}
    for e in [e1, e2, e3, e4]:
        for te in [te1, te2, te3, te4, te5, te6, te7]:
            v = ElemSim.sim(e, te)
            if v < minTmp:
                minTmp = v
                pair = {e.content: te.content}
    global  MIN
    MIN = minTmp
    # targetEdgeList = [edge1, edge2, edge3, edge4]
    # currentGraph = tg1
    # res, ways = connect(tg1,tg8,{})
    # for way in ways:
    #     for e in way:
    #         print(e.target.id)
    source = [g1,g2,g3,g4]
    target = [tg1,tg2,tg3,tg4,tg5,tg6,tg7,tg8,tg9]
    # am = getAM(graphSet)
    # print(connected(0,7,am,[]))
    adjacentMatrix = getAM(target)
    res, pair = graphMatch(source,target,-1, 0, adjacentMatrix)
    for i in range(len(pair)-1):
        fromGraph = pair[i]
        toGraph = pair[i+1]
        score, path = getPath(fromGraph, toGraph, adjacentMatrix, [])
        print('from',fromGraph,'to', toGraph, 'path:', path)

        # print(k, tmp)
        # t_k = target[tmp].elements[0].content
        # print(s_k)
    # print(res)
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