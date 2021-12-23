from json import dumps
import json
import datetime


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def wrap_json_for_send(d: dict, status_code: str, version: str = "0.1", message: str = None) -> str:
    """

    @rtype: object
    """
    d['version'] = version
    d['statusCode'] = status_code
    if message is not None:
        d['message'] = message
    return dumps(d, cls = DateEncoder)
