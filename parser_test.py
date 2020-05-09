import Parser
test_json = "data/a2_b21/a31.json"
t_list = Parser.parse_test_file(test_json)
for t in t_list:
    print(t['event_type'],t)