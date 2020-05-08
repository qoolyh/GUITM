from scoreCount import score_count

srcGroups = [
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a51', 'a52', 'a53', 'a54', 'a55'],
             # ['a51', 'a52', 'a53', 'a54', 'a55'],
             ]
tarGroups = [
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a51', 'a52', 'a53', 'a54', 'a55'],
             # ['a51', 'a52', 'a53', 'a54', 'a55'],
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
cate = ''
srcGroup = ''
tarGroup = ''
haveMatched = {}
for i in range(len(cates)):
    cate = cates[i]
    srcGroup = srcGroups[i]
    tarGroup = tarGroups[i]
    haveMatched = {}
    tmp = cate.split('_')
    score_count(tmp[0], tmp[1], srcGroup, tarGroup, '_oracle_test')
    print('----------')
    score_count(tmp[0], tmp[1], srcGroup, tarGroup, '_noOracle_sim_cal_edge_update')