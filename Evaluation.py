from GlobleData import Gol
from Util import readJson


def res_to_key(res):
    key_set = []
    for r in res:
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



def evaluate(res, path):
    cate1 = Gol.get_value('cate1')
    cate2 = Gol.get_value('cate2')
    src = Gol.get_value('src')
    tgt = Gol.get_value('tgt')
    groundTruthFile = "groundtruth/" + cate1 + "/" + cate2 + "/" + src + "-" + tgt + "-" + cate2 + ".json"
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
