from json import dumps
from flask_sqlalchemy import SQLAlchemy


def wrap_json_for_send(d: dict, status_code: str, version: str = "0.1") -> str:
    d['version'] = version
    d['statusCode'] = status_code
    return dumps(d)


def run_sql(T_sql: str, db: SQLAlchemy):  # 把T_sql放到sql server中运行
    cursor = db.engine.execute(T_sql)
    ret = cursor.fetchall()
    return ret
