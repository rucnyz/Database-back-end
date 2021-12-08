from json import dumps

def wrap_json_for_send(d:tuple, status_code:str, version:str="0.1")->str:
    d['version'] = version
    d['statusCode'] = status_code
    return dumps(d)