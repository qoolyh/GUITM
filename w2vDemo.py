import gensim
from StrUtil import StrUtil

model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit=100000)


def w2v_sim(w_from, w_to):
    # w_from = "".join(list(filter(str.isalpha, w_from)))
    # w_to = "".join(list(filter(str.isalpha, w_to)))
    if w_from.lower() == w_to.lower():
        sim = 1.0
    elif w_from in model.vocab and w_to in model.vocab:
        sim = model.similarity(w1=w_from, w2=w_to)
    else:
        sim = 0
    return sim


def arraySim(strArray, strArray2):
    scores = []
    # valid_new_words = []
    # valid_old_words = copy.deepcopy(strArray2)
    valid_new_words = set()
    valid_old_words = set(strArray2)

    for s1 in strArray:
        for s2 in strArray2:
            sim = w2v_sim(s1, s2)
            if sim:
                valid_new_words.add(s1)
                scores.append((s1, s2, sim))
    scores = sorted(scores, key=lambda x: x[2], reverse=True)
    counted = []
    for new_word, old_word, score in scores:
        if new_word in valid_new_words and old_word in valid_old_words:
            valid_new_words.remove(new_word)
            valid_old_words.remove(old_word)
            counted.append(score)
        if not valid_new_words or not valid_old_words:
            break
    # return sum(counted) / len(strArray) if strArray else 0
    return sum(counted) / len(counted) if counted else 0


def elem_sim(tgt_elem, src_elem):
    v = -1
    if not src_elem:
        return 0
    length = 0


    tgt_id = tgt_elem['resource-id']
    src_id = src_elem['resource-id']

    tgt_txt = tgt_elem['text']
    tgt_cls = tgt_elem['class']
    tgt_desc = tgt_elem['content-desc']

    src_txt = src_elem['text']
    src_cls = src_elem['class']
    src_desc = src_elem['content-desc']

    clsMatch = False
    for k in StrUtil.CLASS_CATEGORY:
        if k in src_cls.lower():
            for cls in StrUtil.CLASS_CATEGORY[k]:
                if cls in tgt_cls.lower():
                    clsMatch = True
                    break
            if clsMatch:
                break
    if tgt_txt.isnumeric() and src_txt.isnumeric():
        contentScore = 1.0
    else:
        contentScore = arraySim(StrUtil.tokenize("text", tgt_txt), StrUtil.tokenize("text", src_txt))
    idScore = arraySim(StrUtil.tokenize("resource-id", tgt_id), StrUtil.tokenize("resource-id", src_id))
    descScore = arraySim(StrUtil.tokenize("content-desc", tgt_desc), StrUtil.tokenize("content-desc", src_desc))
    print(contentScore, idScore, descScore)
    v = contentScore + idScore + descScore  # + clsScore
    v /= 3
    if not clsMatch:
        v -= 0.3
    return v


def main():
    src_elem = {
        "class": "android.widget.EditText",
        "resource-id": "com.android.browser:id/url",
        "text": "https://www.google.com/webhp?client=ms-android-google&source=android-home",
        "content-desc": "",
        "clickable": "true",
        "password": "false",
        "parent_text": "",
        "sibling_text": "",
        "stepping_events": [],
        "package": "com.android.browser",
        "activity": ".BrowserActivity",
        "event_type": "gui",
        "score": 0.30917364147110693,
        "action": [
            "send_keys_and_enter",
            "https://www.ics.uci.edu"
        ]
    }
    tgt_elem = {
        "class": "android.widget.EditText",
        "resource-id": "com.android.browser:id/url",
        "text": "https://www.google.com/webhp?client=ms-android-google&source=android-home",
        "content-desc": "",
        "clickable": "true",
        "password": "false",
        "parent_text": "",
        "sibling_text": "",
        "stepping_events": [],
        "package": "com.android.browser",
        "activity": ".BrowserActivity",
        "event_type": "gui",
        "score": 0.30917364147110693,
        "action": [
            "send_keys_and_enter",
            "https://www.ics.uci.edu"
        ]
    }
    v = elem_sim(tgt_elem, src_elem)
    print(v)


main()
