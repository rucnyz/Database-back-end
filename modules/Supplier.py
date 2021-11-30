from flask import Blueprint,request,current_app
from flask_sqlalchemy import SQLAlchemy
from json import dumps
from utils import run_sql,wrap_json_for_send

supplier = Blueprint('supplier', __name__)
db = SQLAlchemy()

# 商家进行注册,利用所有人的身份证进行登录
# /api/supplier/register
# input:base, { "password", "supplierName", "ownerName", "ownerID"}
# output: base, {”supplier_id“}

@supplier.route("/register", methods=['POST', 'GET'])  # zzm
def register():
    password = request.args['password']
    supplier_name = request.args['supplierName']
    owner_name = request.args['ownerName']
    owner_id = request.args['ownerID']

    getNum = """
     SELECT COUNT(*)
    from supplier   
     """
    tuple_tmp = run_sql(getNum, db)
    supplier_id_new = 'S' + tuple_tmp[0]

    register = """
    INSERT 
    INTO supplier
    VALUES(%s, %s, %s, %s, %s)
    """ % (supplier_id_new, password, supplier_name, owner_name, owner_id)

    db.engine.execute(register)
    new_supp_info = [{"ID": supplier_id_new}]

    return dumps(new_supp_info)

# 商家登录。用户提供登录名与密码，与数据库中内容进行匹配验证，返回登录成功与否。
# /api/supplier/login
# input: base, {"ownerID":"xxx","password:"xxx"}
# output: base, {"suppID":"xxx"}
@supplier.route("/login", methods=['POST', 'GET'])  # zzm
def login():
    owner_id = request.args['ownerID']
    password = request.args['password']
    login = """
    SELECT supplier_id
    FROM supplier
    WHERE supplier = %s AND customer_password = %s
    
    """ % (owner_id, password)

    tuple = run_sql(login, db)
    supp_ID = [{"ID": tuple[0]}]

    return dumps(supp_ID)
