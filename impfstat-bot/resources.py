import util

api_key = util.read_json_file("api-key.json")
strings = util.read_json_file("strings.json")  # Strings einlesen
conf = util.read_json_file("config.json")  # config einlesen
command_file = util.read_json_file("commands.json")
consts = util.read_json_file("constants.json")

commands = command_file["command_list"]
category_list = command_file["categories"]
