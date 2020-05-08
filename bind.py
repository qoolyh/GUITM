import Parser

def get_anchor(dict):
    anchor = {}
    for gid in dict:
        update_anchor(dict[gid], anchor)
    return anchor


def update_anchor(graph, anchor):
    for e in graph.edges:
        evts = e.target
        if isinstance(evts,list):
            for ev in evts:
                if ev.__contains__('inputText'):
                    text = ev['inputText']
                    loc = e.fromGraph
                    if anchor.__contains__(text):
                        anchor[text].append([e,ev])
                    else:
                        anchor[text] = [e,ev]
    return anchor


def get_bind_info(dict):
    bind_info = {}
    anchor = get_anchor(dict)
    for gid in dict:
        graph = dict[gid]
        elems = graph.elements
        for e in elems:
            if anchor.__contains__(e.text):
                if bind_info.__contains__(gid):
                    for edge in anchor[e.text]:
                        if bind_info[gid].index(edge)<0:
                            bind_info[gid].append(edge)
                else:
                    bind_info[gid] = anchor[e.text]
    return bind_info


def graph_update(src_id, tgt_id, src_bind, tgt_bind,tar_dict, match_info):
    if src_bind.__contains__(src_id) and tgt_bind.__contains__(tgt_id):
        if match_info.__contains__(src_id):
            if tgt_bind[tgt_id][1] == match_info[src_id]:
                graph = tar_dict[tgt_id]
                for i in range(len(graph.elements)):
                    e = graph.elements[i]
                    if e.text == tgt_bind[tgt_id][1]['inputText']:
                        tar_dict[tgt_id].elements[i].text = src_bind[src_id][1]['inputText']



def test(src_dict, tgt_dict):
    s_bind = get_bind_info(src_dict)
    t_bind = get_bind_info(tgt_dict)
    sid = -1
    tid = -1
    match_info = {}
    for k in s_bind:
        sid = k
        e = s_bind[k][1]
        for l in t_bind:
            tid = l
            te = t_bind[l][1]
            match_info = {k:te}
            break
        break
    for e in tgt_dict[tid].elements:
        print(e.text)
    graph_update(sid, tid, s_bind, t_bind, tgt_dict, match_info)
    for e in tgt_dict[tid].elements:
        print(e.text)


cate = 'a2_b22'
src = 'a24'
tgt = 'a22'
src_dict = Parser.parseJson2STG("data/" + cate + "/src/" + src + "/activitiesSummary.json")
tgt_dict = Parser.parseJson2STG("data/" + cate + "/tar/" + tgt + "/activitiesSummary.json")

test(src_dict, tgt_dict)
