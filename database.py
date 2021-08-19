import json

def read():
    db = None
    with open('db.json', 'r') as f:
        db = json.load(f)
    return db

def write(json_obj):
    with open('db.json', 'w') as f:
        f.write(json.dumps(json_obj, indent=4))