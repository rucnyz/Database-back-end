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
    customer_id_new = 'C' + str(int(t['cnt'][0]) + 1)

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

    t = run_sql(login)[0].values()[0]
    cust_ID = {"ID": t}

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
    WHERE customer_id='%s'
    """ % id
    tuple = run_sql(select_customer_info)
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
    run_sql(add_customer_info)
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
    WHERE customer_id='%s', address_name='%s'
    """ % (id, address)
    run_sql(delete_customer_info)
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
    SET address_name='%s', nickname='%s', phone='%s'
    WHERE customer_id='%s'
    """ % (nickname, address, phone_number, id)
    run_sql(update_customer_info)
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
    WHERE p.product_id = c.product_id AND c.customer_id='%s'
    """ % id
    t = run_sql(select_cart)
    column = ["productID", "pic_url", "count", "productName"]
    data_list = [dict(zip(column, t[i])) for i in range(len(t))]
    d = {"total number": len(t), "detail": data_list}
    return wrap_json_for_send(d, 'successful')


# /api/customer/id/shoppingCart/update  仅限更新数量
# input:base, {"customerID": "xxx", "productID":,"商品数量"}
# output:base
# 从购物车进入订单界面，与从顾客界面进入订单相同。
@customer.route("/<id>/shoppingCart/update", methods = ['POST'])  # hcy
def update_cart(id):
    product_id = request.json['productID']
    count = request.json['count']
    update_cart = """
    UPDATE cart
    SET count=%d
    WHERE customer_id='%s', product_id='%s'
    """ % (count, id, product_id)
    run_sql(update_cart)
    d = {}
    return wrap_json_for_send(d, 'successful')


# /api/customer/id/shoppingCart/delete  删除购买的这一整个商品
# input: base,{"customerID": "xxx", "productID":}
# output: base
# 下订单后，删除购物车中购买的商品
@customer.route("/<id>/shoppingCart/delete", methods = ['POST'])  # hcy
def delete_cart(id):
    product_id = request.json['productID']
    delete_cart = """
    DELETE
    FROM cart
    WHERE customer_id='%s', product_id='%s'
    """ % (id, product_id)
    run_sql(delete_cart)
    d = {}
    return wrap_json_for_send(d, 'successful')


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
    t = run_sql(set_is_return, )
    d = {}
    return wrap_json_for_send(d, "successful")


# 从购物车里添加新订单。
# /api/customer/<id>/orders/add_cart
# input:base,{"supplierID","productID","orderDate","priceSum","quantity","deliverAddress","receiveAddress"}
# output:base, {"ordersID"}
#
@customer.route("/<id>/orders/add_cart", methods = ['POST', 'GET'])  # zzm
def orders_add_cart(id):  # 新订单添加
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
    tuple_tmp = run_sql(getNum)
    order_id_new = 'O' + str(int(tuple_tmp['cnt'][0] + 1))  # 获得新的订单编号

    orders_add = """
    INSERT
    INTO orders
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """ % (
        order_id_new, id, supplier_id, product_id, order_date, price_sum, quantity, deliver_address, receive_address, 0,
        "Null")

    run_sql(orders_add)
    new_order_info = {"ID": order_id_new}

    return wrap_json_for_send(new_order_info, "successful")


# 从商品界面里添加新订单。除接口外，与购物车添加订单均相同。
# /api/customer/<id>/orders/add_product
# input:base,{"supplierID","productID","orderDate","priceSum","quantity","deliverAddress","receiveAddress"}
# output:base, {"ordersID"}
#
@customer.route("/<id>/orders/add_product", methods = ['POST', 'GET'])  # zzm
def orders_add_product(id):  # 新订单添加
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
    tuple_tmp = run_sql(getNum)
    order_id_new = 'O' + str(int(tuple_tmp['cnt'][0] + 1))  # 获得新的订单编号

    orders_add = """
    INSERT
    INTO orders
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """ % (
        order_id_new, id, supplier_id, product_id, order_date, price_sum, quantity, deliver_address, receive_address, 0,
        "Null")

    run_sql(orders_add)
    new_order_info = {"ID": order_id_new}

    return wrap_json_for_send(new_order_info, "successful")
