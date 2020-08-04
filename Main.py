from GBMT_0509 import GBTM
from GlobleData import *
import Parser_me as Parser
from Init import initAll

srcGroups = [
             # ['a12'],
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             # ['a31', 'a32', 'a33', 'a35'],G
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a51', 'a52', 'a53', 'a54', 'a55']
             # ['a51', 'a52', 'a53', 'a54', 'a55']
             ]
tarGroups = [
             # ['a13'],
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22','a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a51', 'a52', 'a53', 'a54', 'a55']
             # ['a51', 'a52', 'a53', 'a54', 'a55']
             ]
srcFolder = ''
tarFolder = ''
cates = [
         # 'a1_b11',
         # 'a1_b12',
         'a2_b21',
         'a2_b22',
         # 'a3_b31',
         # 'a3_b32',
         # 'a4_b41',
         # 'a4_b42',
         # 'a5_b51',
         # 'a5_b52'
        ]
start_act = {
    'a21':'com.rubenroy.minimaltodo.MainActivity0',
    'a22': 'douzifly.list.ui.home.MainActivity0',
    'a23':'org.secuso.privacyfriendlytodolist.view.MainActivity0',
    'a24':'kdk.android.simplydo.SimplyDoActivity0',
    'a25':'com.woefe.shoppinglist.activity.MainActivity0'
}
cate = ''
srcGroup = ''
tarGroup = ''
haveMatched = {}
for i in range(len(cates)):
    cate = cates[i]
    srcGroup = srcGroups[i]
    tarGroup = tarGroups[i]
    haveMatched = {}
    for src in srcGroup:
        srcFolder = src
        for tar in tarGroup:
            tarFolder = tar
            if src != tar:
                haveMatched = {}
                eSim = {}
                cache = {}
                pair = src + '_' + tar
                # pair = 'a31_a35'
                sim_json = "data/" + cate + "/sim_" + src + ".json"
                # sim_json = "data/sim_a31.json"
                src_json = "data/" + cate + "/src/" + src + "/activitiesSummary.json"
                # src_json = "data/src/a31/activitiesSummary.json"
                tar_json = "data/" + cate + "/tar/" + tar + "/activitiesSummary.json"
                # tar_json = "data/tar/a35/activitiesSummary.json"
                test_json = "data/" + cate + "/" + src + ".json"
                tgt_start = start_act[tar]

                initAll(src_json, tar_json, test_json, sim_json, pair, tgt_start, cate, src, tar)
                print('running...src=',src,' tgt=',tar)
                GBTM()