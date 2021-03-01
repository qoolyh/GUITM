DP_res = {}


def basicDP(list1, list2, start1, start2, func, init=False):
    if init:
        DP_res.clear()
    max = 0
    record = []
    i = start1 + 1
    rec_i = []
    score_i = 0
    match_i = -1
    if i < len(list1):
        for j in range(start2 + 1, len(list2)):
            key = str(i) + '_' + str(j)
            if key in DP_res:
                max_i, record_i = DP_res[key]
                if max < max_i:
                    max = max_i
                    record = record_i
                continue
            v = func(list1[i], list2[j])
            left, left_rec = basicDP(list1, list2, i, j, func)
            left_ban, left_rec_ban = basicDP(list1, list2, i, start2, func)
            left_kpt, left_rec_kpt = basicDP(list1, list2, start1, j, func)
            if max <= v + left:
                max = v + left
                record = [j] + left_rec
            if max <= left_kpt:
                max = left_kpt
                record = left_rec_kpt
            if max <= left_ban:
                max = left_ban
                record = [-1] + left_rec_ban
            DP_res.update({key: [max, record]})
    return max, record


class SeqMatcher:
    @staticmethod
    def seq_match(src_STL, tgt_STL):
        match_res = []
        score = 0

        return score, match_res


    def seq_sim(sub_STL1, sub_STL2):
        score = 0
        match_res = []


