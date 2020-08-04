import json
import os

from GlobleData import Gol


def records(res, path):
    cate1 = Gol.get_value('cate1')
    cate2 = Gol.get_value('cate2')
    src = Gol.get_value('src')
    tgt = Gol.get_value('tgt')
    path_dir = 'result/'+cate1+'/'+cate2+'/'+src+'_'+tgt+'_path.json'
    res_dir = 'result/' + cate1 + '/' + cate2 + '/' + src + '_' + tgt + '_res.json'
    dir = 'result/'+cate1+'/'+cate2+'/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(path_dir, 'w') as pf:
        json.dump(path_to_json(path), pf)
        pf.close()
    with open(res_dir, 'w') as rf:
        json.dump(res, rf)
        rf.close


def path_to_json(path):
    path_array = []
    for p in path:
        e_list = p.target
        for e in e_list:
            if isinstance(e, list):
                for e_i in e:
                    path_array.append(e_i)
            else:
                path_array.append(e)
    return path_array