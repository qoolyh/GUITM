import gensim

from StrUtil import StrUtil

model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit= 500000)

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



def elem_sim(src_elem, tgt_elem):
    content = 0
    id_desc = 0
    tgt_id = ''
    src_id = ''
    if src_elem["action"][0] == "KEY_BACK" or  tgt_elem["type"] == "back":
        return 1 if src_elem["action"][0] == "KEY_BACK" and tgt_elem["type"] == "back" else 0
    else:
        tgt_txt = tgt_elem['text']
        tgt_cls = tgt_elem['class']
        tgt_desc = tgt_elem['content-desc']

        src_txt = src_elem['text']
        src_cls = src_elem['class']
        src_desc = src_elem['content-desc']

        if tgt_txt.isnumeric() and src_txt.isnumeric():
            content = 1.0

        if tgt_elem['resource-id'].find("/") != -1:
            tgt_id = tgt_elem['resource-id'].split("/")[1]
        else:
            tgt_id = tgt_elem['resource-id']

        if src_elem['resource-id'].find("/") != -1:
            src_id = src_elem['resource-id'].split("/")[1]
        else:
            src_id = src_elem['resource-id']

        tgt_token = (StrUtil.tokenize("content-desc", tgt_desc))+(StrUtil.tokenize("resource-id", tgt_id))
        src_token = (StrUtil.tokenize("content-desc", src_desc))+(StrUtil.tokenize("resource-id", src_id))
        id_desc = arraySim(tgt_token, src_token)
        if content != 1.0:
            content = arraySim(StrUtil.tokenize("text", src_txt), StrUtil.tokenize("text", src_txt))
        v = id_desc + content

        if 'send_keys' in src_elem['action']:
            if 'EditText' in tgt_elem['class']:
                return id_desc
            else:
                return 0
        else:
            clsMatch = False
            for key in StrUtil.CLASS_CATEGORY:
                if key in src_cls.lower():
                    for cls in StrUtil.CLASS_CATEGORY[key]:
                        if cls in tgt_cls.lower():
                            clsMatch = True
                            break
                    if clsMatch:
                        break
            if not clsMatch:
                v -= 0.3
            return v

