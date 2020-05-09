from nltk.corpus import wordnet as wn
from itertools import product

class ElemSim:
    def __init__(self, e1, e2):
        self.sim = sim(e1,e2)




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