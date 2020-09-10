# from GBMT_0509 import GBTM
# from GlobleData import *
# import Parser_me as Parser
from Init import initAll
from UBTM import UBTM

srcGroups = [
             # [ 'a15'],
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a51', 'a52', 'a53', 'a54', 'a55'],
             # ['a51', 'a52', 'a53', 'a54', 'a55']
             ]
tarGroups = [
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             # ['a11', 'a12', 'a13', 'a14', 'a15'],
             ['a21', 'a22','a23', 'a24', 'a25'],
             ['a21', 'a22', 'a23', 'a24', 'a25'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a31', 'a32', 'a33', 'a35'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a41', 'a42', 'a43', 'a44', 'a45'],
             # ['a51', 'a52', 'a53', 'a54', 'a55'],
             # ['a51', 'a52', 'a53', 'a54', 'a55']
             ]
srcFolder = ''
tarFolder = ''
cates = [
         # 'a1_b11',
         # 'a1_b12',
         'a2_b21',
         'a2_b22'
         # 'a3_b31',
         # 'a3_b32',
         # 'a4_b41',
         # 'a4_b42',
         # 'a5_b51',
         # 'a5_b52'
        ]
start_act = {
    'a11':'acr.browser.lightning.MainActivity8',
    'a12':'com.ijoysoft.browser.activity.ActivityMain0',
    'a13':'com.stoutner.privacybrowser.activities.MainWebViewActivity0',
    'a14':'de.baumann.browser.Activity.BrowserActivity0',
    'a15':'org.mozilla.focus.activity.MainActivity0',

    'a21':'com.rubenroy.minimaltodo.MainActivity0',
    'a22': 'douzifly.list.ui.home.MainActivity0',
    'a23':'org.secuso.privacyfriendlytodolist.view.MainActivity0',
    'a24':'kdk.android.simplydo.SimplyDoActivity0',
    'a25':'com.woefe.shoppinglist.activity.MainActivity0',

    'a31':'com.contextlogic.wish.activity.login.LoginActivity0',
    'a32':'com.contextlogic.wish.activity.login.createaccount.CreateAccountActivity0',
    'a33':'com.rainbowshops.activity.MainActivity0',
    'a34':'',
    'a35':'com.yelp.android.nearby.ui.ActivityNearby0',

    'a41': 'com.fsck.k9.activity.MessageList0',
    'a42': 'com.fsck.k9.activity.MessageList0',
    'a43': 'ru.mail.mailapp.MailRuLoginActivity0',
    'a44': 'ru.mail.mailapp.MailRuLoginActivity0',
    'a45': 'ru.mail.mailapp.MailRuLoginActivity0',

    'a51': 'anti.tip.tip0',
    'a52': 'com.appsbyvir.tipcalculator.MainActivity0',
    'a53': 'com.tleapps.simpletipcalculator.MainActivity0',
    'a54': 'com.zaidisoft.teninone.Calculator0',
    'a55': 'com.jpstudiosonline.tipcalculator.MainActivity0'
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
                UBTM()