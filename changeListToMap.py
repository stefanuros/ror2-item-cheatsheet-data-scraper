import json

my_file = open("out/itemData.json", "r")
itemDataList = json.load(my_file)

items = {}

for item in itemDataList:
    print(item["name"])
    items[item["name"]] = item

with open("out/items.json", "w") as f:
    f.write(json.dumps(items))
