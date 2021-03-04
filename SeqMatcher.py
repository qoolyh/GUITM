
import math
import simCal


DP_res = {}


def jump_cost(v1, v2):
    return math.log(abs(v1 - v2) + 1, 2) + 1


def basicDP(list1, list2, start1, start2, func, prev1, prev2, init=False):
    if init:
        DP_res.clear()
        max, record = basicDP(list1, list2, 0, 0, func, 0, 0)
        tmp_record = [0] + record
        DP_res.update({'0_0': tmp_record})
        return max, record
    if start1 == len(list1) - 2 or start2 == len(list2) - 2:
        jump1 = start1 - prev1 + 1
        jump2 = start2 - prev2 + 1
        key = str(start1 + 1) + '_' + str(start2 + 1)
        if key in DP_res:
            max, record = DP_res[key]
        else:
            max = jump_cost(jump1, jump2)
            record = []
            for n in range(start1 + 1, len(list1)):
                record.append(-1)
        return max, record
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
            v = func(list1[i], list2[j]) * jump_cost(i - prev1, j - prev2)
            left, left_rec = basicDP(list1, list2, i, j, func, i, j)  # i matched to j, so prev1 =i, prev2 = j
            left_ban, left_rec_ban = basicDP(list1, list2, i, start2, func, prev1, prev2)  # ban i, so prev1 kept
            left_kpt, left_rec_kpt = basicDP(list1, list2, start1, j, func, prev1, prev2)
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
    def seq_match(src_STL, tgt_STL, stg):
        global STG
        STG = stg
        func = SeqMatcher.state_sim
        score, res = basicDP(src_STL, tgt_STL, 0, 0, func, 0, 0, True)
        return score, res

    @staticmethod
    def state_sim(state1, edges2):
        score = 0
        edge1 = state1.edges
        chosen_edge = []
        event1 = edge1
        if isinstance(event1, list):
            event1 = event1[-1]
        for edge2 in edges2:
            event2 = edge2.target
            if isinstance(event2, list):
                event2 = event2[-1]
            if isinstance(event2, list):
                event2 = event2[-1]
            esim = simCal.single_elem_sim(event1, event2)
            gsim = simCal.gSim_baseline(state1.elements, STG[edge2.fromGraph].elements)
            if esim + gsim > score:
                score = esim + gsim
                chosen_edge = edge2
        return score


