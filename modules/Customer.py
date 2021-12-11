# zzm

from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

customer = Blueprint('customer', __name__)

db = SQLAlchemy()


@customer.route("/register", methods = ['POST', 'GET'])  # zzm
def register():
    phone_number = request.json['phoneNumber']
    password = request.json['password'][:10]

    getNum = """
     SELECT COUNT(*) as cnt
    from customer   
     """
    t = run_sql(getNum)
    customer_id_new = 'C' + str(int(t['cnt'][0])+1)

    register = """
    INSERT 
    INTO customer
    VALUES('%s','%s','%s')
    """ % (customer_id_new, phone_number, password)

    _ = run_sql(register)
    new_cust_info = {"ID": customer_id_new}

    return wrap_json_for_send(new_cust_info, "successful")


# 用户登录。用户提供登录名与密码，与数据库中内容进行匹配验证，返回登录成功与否。
# /api/user/login
# input: base, {"phoneNumber":"xxx","password:"xxx"}
# output: base, {"ID":"xxx"}
@customer.route("/login", methods = ['POST', 'GET'])
def login():
    phone_number = request.json['phoneNumber']
    password = request.json['password'][:10]
    print(password)
    login = """
    SELECT customer_id
    FROM customer
    WHERE customer_phonenumber='%s' AND customer_password='%s'
    """ % (phone_number, password)

    t = run_sql(login)
    cust_ID = {"ID": t['customer_id'][0]}

    return wrap_json_for_send(cust_ID, "successful")


# 用户个人信息查询
# /api/customer/ID:"xxx"/info
# input : base, {"ID":"xxx"}
# output: base, {"nickName":"xxx", "phoneNumber":"xxx","address":list(无则返回空); }
@customer.route("/<id>/info", methods = ['POST'])  # hcy
def select_customer_info(id):
    # content = request.json
    select_customer_info = """
    SELECT nickname, phone, address_name
    FROM info_customer
    WHERE customer_id = %s
    """ % id
    tuple = run_sql(select_customer_info, db)
    column = ['nickName', 'phoneNumber', 'address']
    list = [dict(zip(column, tuple[i])) for i in range(len(tuple))]
    d = {"detail": list}
    return wrap_json_for_send(d, 'successful')


# /api/customer/"id"/address/add
# input:base,{"ID","nickName","address","phoneNumber"}
# output: base
@customer.route("/<id>/address/add", methods = ['POST'])  # hcy
def add_customer_info(id):
    nickname = request.json['nickName']
    address = request.json['address']
    phone_number = request.json['phoneNumber']

    add_customer_info = """
    INSERT
    INTO info_customer(customer_id, address_name, nickname, phone)
    VALUES('%s', '%s', '%s', '%s')
    """ % (id, nickname, address, phone_number)
    run_sql(add_customer_info, db)
    d = {}
    return wrap_json_for_send(d, "successful")


# /api/customer/"id"/address/delete
# input: base,{"ID","address"}
# output: base
@customer.route("/<id>/address/delete", methods = ['POST'])  # hcy
def delete_customer_info(id):
    address = request.json['address']
    delete_customer_info = """
    DELETE
    FROM info_customer
    WHERE customer_id = %s, address_name = %s
    """ % (id, address)
    run_sql(delete_customer_info, db)
    d = {}
    return wrap_json_for_send(d, "successful")


# /api/customer/"id"/address/update
# input: base, {"ID","nickName","phoneNumber","address"}
# ouput: base
@customer.route("/<id>/address/update", methods = ['POST'])  # hcy
def update_customer_info(id):
    nickname = request.json['nickName']
    address = request.json['address']
    phone_number = request.json['phoneNumber']
    update_customer_info = """
    UPDATE info_customer
    SET address_name = %s, nickname = %s, phone = %s
    WHERE customer_id = %s
    """ % (nickname, address, phone_number, id)
    run_sql(update_customer_info, db)
    d = {}
    return wrap_json_for_send(d, "successful")


# 2. 用户购物车查询
# /api/customer/"id"/shoppingCart
# input: base,"ID"
# output: base,{"total number", "detail":[{"productID","pic_url",”count“,"productName"},...,{...}]}
@customer.route("/<id>/shoppingCart", methods = ['POST'])  # hcy
def select_cart(id):
    select_cart = """
    SELECT p.product_id, pic_url, count, product_name
    FROM product p, cart c
    WHERE p.product_id = c.product_id AND c.customer_id = %s
    """ % id
    t = run_sql(select_cart, db)
    column = ["productID", "pic_url", "count", "productName"]
    data_list = [dict(zip(column, t[i])) for i in range(len(t))]
    d = {"total number": len(t), "detail": data_list}
    return wrap_json_for_send(d, 'successful')


# /api/customer/"id"/shoppingCart/add
# input: base,{"用户ID": "xxx", "商品ID":,"商品数量"}
# output:base
@customer.route("/<id>/shoppingCart", methods = ['POST'])  # hcy
# @TODO: IF EXIST

# 3. 用户已有订单查询。返回用户已有订单。允许顾客进行退货处理。
@customer.route("/<id>/orders", methods = ['POST'])  # lsy
def get_orders(id):
    content = request.json
    ## 提取信息
    get_orders = """
    SELECT order_id, p.product_id, product_name, quantity 
    FROM product p, orders o
    WHERE o.customer_id = '%s' 
    AND p.product_id = o.product_id;
    """ % id
    t = run_sql(get_orders)
    column = ['orderID', 'productID', 'productID', 'quantity']
    d = [dict(zip(column, t[i])) for i in range(len(t))]
    d = {"number": len(t), "detail": d}
    return wrap_json_for_send(d, "successful")


@customer.route("/<id>/orders/salesreturn", methods = ['POST'])  # lsy
def set_is_return(id):  # 设置退货标记
    order_id = request.json["order_id"]
    set_is_return = """
    UPDATE orders
    SET is_return = 1 
    WHERE order_id = '%s' ;
    """ % order_id
    t = run_sql(set_is_return,)
    d = {}
    return wrap_json_for_send(d, "successful")


# 从购物车里添加新订单。
# /api/customer/<id>/orders/add
# input:base,{"supplierID","productID","orderDate","priceSum","quantity","deliverAddress","receiveAddress"}
# output:base, {"ordersID"}
#
@customer.route("/<id>/orders/add", methods = ['POST', 'GET'])  # zzm
def orders_add(id):  # 新订单添加
    supplier_id = request.json["supplierID"]
    product_id = request.json["productID"]
    order_date = request.json["orderDate"]
    price_sum = request.json["priceSum"]
    quantity = request.json["quantity"]
    deliver_address = request.json["deliverAddress"]
    receive_address = request.json["receiveAddress"]

    getNum = """
     SELECT COUNT(*) as cnt
    from orders  
     """
    tuple_tmp = run_sql(getNum, db)
    order_id_new = 'O' + str(int(tuple_tmp['cnt'][0]+1)) # 获得新的订单编号

    orders_add = """
    INSERT
    INTO orders
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """ % (
        order_id_new, id, supplier_id, product_id, order_date, price_sum, quantity, deliver_address, receive_address, 0,
        "Null")

    run_sql(orders_add, db)
    new_order_info = {"ID": order_id_new}

    return wrap_json_for_send(new_order_info, "successful")
