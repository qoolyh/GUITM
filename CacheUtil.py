import json


def read_cache(dir):
    res = json.loads(dir)
    return res


def write_cache(dir, json_res):
    with open(dir, 'w') as file_obj:
        json.dump(json_res, file_obj)
