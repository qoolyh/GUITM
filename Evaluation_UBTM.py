import json

from GlobleData import Gol
from Util import readJson


def res_to_key(res):
    key_set = []
    for r in res:
        if r == "null":
            continue
        key = r['resource-id']+'_'+r['class']+'_'+r['content-desc']
        key_set.append(key)

    return key_set


def path_to_key(path):
    key_set = []
    for p in path:
        e_list = p.target
        for e in e_list:
            if isinstance(e, list):
                for e_i in e:
                    print(e_i)
                    key = e_i['resource-id'] + '_' + e_i['class'] + '_' + e_i['content-desc']
                    key_set.append(key)
            else:
                key = e['resource-id'] + '_' + e['class'] + '_' + e['content-desc']
                key_set.append(key)
    return key_set


def getOracleGnd(test_file):
    oracles = []
    test = readJson(test_file)
    for t in test:
        if t['event_type'] == 'oracle':
            oracles.append(t)
    return oracles


def oracle_precision(oracle_gnd, oracle_res):
    i=0
    correct = 0
    print(len(oracle_gnd), len(oracle_res))
    for o_gnd in oracle_gnd:
        o_res = oracle_res[i]
        i+=1
        same = False
        if ('text' in o_gnd['action'][0]):
            same  = o_res['txt'] in o_gnd['action'][3]
        else:
            same = o_res['id'] == o_gnd['resource-id'] and o_res['cls'] == o_gnd['class'] and o_res['desc'] == o_gnd['content-desc']
        if same:
            correct += 1
    return correct


def evaluate(res, path, oracle):
    cate1 = Gol.get_value('cate1')
    cate2 = Gol.get_value('cate2')
    src = Gol.get_value('src')
    tgt = Gol.get_value('tgt')
    groundTruthFile = "groundtruth/" + cate1 + "/" + cate2 + "/" + src + "-" + tgt + "-" + cate2 + ".json"
    oracleFile = "groundtruth/" + cate1 + "/" + cate2 + "/" +tgt+".json"

    o_res = getOracleGnd(oracleFile)
    gnd_res = readJson(groundTruthFile)
    pre = 0
    rec = 0

    res_k = res_to_key(res)
    path_k = path_to_key(path)
    gnd_k = res_to_key(gnd_res)


    print('res_k')
    print(res_k)
    print('path_k')
    print(path_k)
    print('gnd_k')
    print(gnd_k)
    for gnd in gnd_k:
        if gnd in res_k:
            pre+=1
        if gnd in path_k:
            rec+=1

    precision = pre/len(res_k)
    recall = rec/len(gnd_k)
    print(precision, recall)

def cal(res_k, path_k, gnd_k):
    pre = 0
    rec = 0
    for gnd in gnd_k:
        if gnd in res_k:
            pre+=1
        if gnd in path_k:
            rec+=1
    return pre, rec


def evaluation_total(cate1, cate2, sets):
    total_res = 0
    total_path = 0
    total_gnd = 0
    total_pre = 0
    total_rec = 0
    total_o_c = 0
    total_o = 0
    for src in sets:
        for tgt in sets:
            if src == tgt:
                continue
            gnd = readJson("groundtruth/" + cate1 + "/" + cate2 + "/" + src + "-" + tgt + "-" + cate2 + ".json")
            res = readJson("result_UBTM/"+cate1+'/'+cate2+'/'+src+'_'+tgt+'_res.json')
            path = readJson("result_UBTM/" + cate1 + '/' + cate2 + '/' + src + '_' + tgt + '_path.json')

            o_gnd = getOracleGnd("data/" + cate1 + "_" + cate2 + "/" + tgt + ".json")
            o_res = readJson("result_UBTM/" + cate1 + '/' + cate2 + '/' + src + '_' + tgt + '_oracle.json')
            corr = oracle_precision(o_gnd, o_res)
            total_o_c += corr
            total_o += len(o_gnd)

            res_key = res_to_key(res)
            path_key = res_to_key(path)
            gnd_key = res_to_key(gnd)
            total_res += len(res_key)
            total_gnd += len(gnd_key)
            pre, rec = cal(res_key, path_key, gnd_key)
            total_pre+= pre
            total_rec += rec
    precision = total_pre / total_res
    recall = total_rec / total_gnd
    o_acc = total_o_c/total_o
    print(precision, recall, o_acc)


evaluation_total('a2','b21', ['a21', 'a22','a23', 'a24', 'a25'])



