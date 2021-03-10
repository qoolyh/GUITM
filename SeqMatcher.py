import math
import simCal


DP_res = {}

def basicDP(list1, list2, start1, start2, func, prev1, prev2, init=False):
    if init:
        DP_res.clear()
        # max, record = basicDP(list1, list2, 0, 0, func, 0, 0)
        # tmp_record = [0] + record
        # DP_res.update({'0_0': tmp_record})
        # return max, tmp_record
    # if start1 == len(list1) - 2 or start2 == len(list2) - 2:
    #     jump1 = start1 - prev1 + 1
    #     jump2 = start2 - prev2 + 1
    #     key = str(start1 + 1) + '_' + str(start2 + 1)
    #     if key in DP_res:
    #         max, record = DP_res[key]
    #     else:
    #         max = jump_cost(jump1, jump2)
    #         record = []
    #         for n in range(start1 + 1, len(list1)):
    #             record.append(-1)
    #     return max, record
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
            if i == len(list1)-1:
                return SeqMatcher.jump_cost(i - prev1, j - prev2), []
            v = func(list1[i], list2[j]) * SeqMatcher.jump_cost(i - prev1, j - prev2)
            # v = func(list1[i], list2[j])
            left, left_rec = basicDP(list1, list2, i, j, func, i, j)  # i matched to j, so prev1 =i, prev2 = j
            left_ban, left_rec_ban = basicDP(list1, list2, i, start2, func, prev1, prev2)  # ban i, so prev1 kept
            left_kpt, left_rec_kpt = basicDP(list1, list2, start1, j, func, prev1, prev2)
            if len(list1[i].edges)>0:
                tmp = list2[j].target[-1]
                if isinstance(tmp, list):
                    tmp = tmp[-1]
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
    def seq_match(src_STL, tgt_STL, stg, ipt_res, start = False):
        global STG
        STG = stg
        func = SeqMatcher.state_sim
        score = 0
        res = []
        global ipt_tgt
        global ipt_src
        ipt_tgt= len(ipt_res)
        tmp_src = []
        for k in ipt_res:
            ipts = ipt_res[k]
            for i in ipts:
                if i['activity'] not in tmp_src:
                    tmp_src.append(i['activity'])
        ipt_src = len(tmp_src)
        if start:
            max = 0
            res = []
            for k in range(-1, len(tgt_STL)-1):
                tmp_score , tmp_res = basicDP(src_STL, tgt_STL, -1, k, func, 0, k+1, True)
                if tmp_score > max:
                    max = tmp_score
                    res = tmp_res
            res.append(len(tgt_STL) - 1)
        else:
            score, res = basicDP(src_STL, tgt_STL, -1, -1, func, 0, 0, True)
        return score, res

    @staticmethod
    def state_sim(state1, edge2):
        score = 0
        edge1 = state1.edges
        chosen_edge = []
        event1 = edge1
        empty = False
        if isinstance(event1, list):
            if len(event1)>0:
                event1 = event1[-1]
            else:
                empty = True
        event2 = edge2.target
        if isinstance(event2, list):
            if len(event2) > 0:
                event2 = event2[-1]
            else:
                empty = True
        if isinstance(event2, list):
            event2 = event2[-1]
        esim = simCal.single_elem_sim(event1, event2) if not empty else 0
        gsim = simCal.graphsim_simple(state1.elements, STG[edge2.fromGraph].elements)
        if esim + gsim > score:
            score = esim + gsim/4
            chosen_edge = edge2
        return score

    @staticmethod
    def jump_cost(v1, v2):
        v1 = max(v1-ipt_src, 0)
        v2 = max(v2-ipt_tgt, 0)
        return 1 / (math.log(abs(v1 - v2) + 1, 2) + 1)