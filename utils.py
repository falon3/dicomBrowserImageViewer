import json

def file_get_contents(filename):
    with open(filename) as f:
        return f.read()
    
def json_encode_list(l):
    newList = []
    for obj in l:
        newList.append(obj.__dict__)
    return json.dumps(newList)
