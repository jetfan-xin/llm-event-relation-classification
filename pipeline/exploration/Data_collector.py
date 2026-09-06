import requests
import json
rel_dic = {}
relations = ["Causes", "HasSubevent", "HasFirstSubevent", "HasLastSubevent"]
for rel in relations:
    rel_dic[rel] = []
    for offset in range(0, 10000, 1000):
        obj = requests.get(f'http://api.conceptnet.io/r/{rel}?offset={str(offset)}&limit=1000').json()
        count = 0
        for edge in obj['edges']:
            if edge['start']['language'] == 'en':
                object = {
                    "start": edge['start'],
                    "end": edge['end'],
                    "text": edge['surfaceText'],
                }
                rel_dic[rel].append(object)
                count += 1
with open('semantic-networks/output.json', 'a') as f:
    json.dump(rel_dic, f, indent = 4)
print(count)

