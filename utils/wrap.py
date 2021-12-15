from json import dumps

def wrap_json_for_send(d:dict, status_code:str, version:str="0.1")->str:
    """

    @rtype: object
    """
    d['version'] = version
    d['statusCode'] = status_code
    return dumps(d)