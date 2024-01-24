import json

test_data = open("json/test_data.json", "r")
json_data = test_data.read()
test_data.close()

game_servers = json.loads(json_data)
