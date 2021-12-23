from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy
import re
from utils import run_sql, wrap_json_for_send

customer = Blueprint('customer', __name__)

db = SQLAlchemy()


# /api/customer/register[已测试]
# input: base, { "phoneNumber":"xxx", "password": "xxx"}
# output:base {"ID":"xxx"}
@customer.route("/register", methods=['POST', 'GET'])  # zzm
def register():
    phone_number = request.json['phoneNumber']
    password = request.json['password'][:10]
#    realName = request.json['realName']
    nickName = request.json['nickName']

    getNum = """
    SELECT COUNT(*) as cnt
    from customer   
    """
    t = run_sql(getNum)
    customer_id_new = 'C' + str(int(t[0]['cnt']) + 1).zfill(9)

    register = """
    INSERT 
    INTO customer
    VALUES(:customer_id_new, :phone_number, :password)
    """

    register_info = """
    INSERT 
    INTO info_customer
    VALUES(:customer_id_new, null , :nickName,:phone_number)
    """
    try:
        _ = run_sql(register, {"customer_id_new":customer_id_new, "phone_number": phone_number, "password": password})
        _ = run_sql(register_info,{"customer_id_new": customer_id_new,"nickName":nickName, "phone_number":phone_number})
        statuscode = "successful"
        new_cust_info = {"ID": customer_id_new}
    except:
        statuscode = "failed"
        new_cust_info = {}

    return wrap_json_for_send(new_cust_info, statuscode)


# 用户登录。用户提供登录名与密码，与数据库中内容进行匹配验证，返回登录成功与否。[已测试]
# /api/user/login
# input: base, {"phoneNumber":"xxx","password:"xxx"}
# output: base, {"ID":"xxx"}
@customer.route("/login", methods=['POST', 'GET'])
def login():
    phone_number = request.json['phoneNumber']
    password = request.json['password'][:10]
    login = """
    SELECT customer_id
    FROM customer
    WHERE customer_phonenumber=:customer_phonenumber AND customer_password=:customer_password
    """
    t = run_sql(login, {"customer_phonenumber": phone_number,
                        "customer_password": password})
    if (len(t) == 0):
        out = {}
        statuscode = "failed"
    else:
        customer_id = t[0]['customer_id']
        info = """
            SELECT nickname, address_name
            FROM info_customer
            WHERE customer_id=:customer_id
            """
        c_info = run_sql(info, {"customer_id": customer_id})
        nickName = c_info[0]['nickname']
        address_name = c_info[0]['address_name']
        out = {"ID": customer_id, "phoneNumber": phone_number, "nickName": nickName, "addressName": address_name}
        statuscode = "successful"

    return wrap_json_for_send(out, statuscode)


# 用户个人信息查询[已测试]
# /api/customer/ID:"xxx"/info
# input : base, {"ID":"xxx"}
# output: base, {"address":[{"nickName","phoneNumber","address"}]}
@customer.route("/<id>/info", methods = ['POST', 'GET'])  # hcy#zzm修改
def select_customer_info(id):
    select_customer_info = """
    SELECT nickname, phone, address_name
    FROM info_customer
    WHERE customer_id=:customer_id
    """
    t = run_sql(select_customer_info, {"customer_id": id})

    column = ['nickName', 'phoneNumber', 'addressName']

    list = [dict(zip(column, t[i].values())) for i in range(len(t))]
    d = {"address": list}
    return wrap_json_for_send(d, 'successful')


# /api/customer/"id"/address/add[已测试]
# input:base,{"customerID","nickName","phoneNumber","address"}
# output: base
@customer.route("/<customerID>/address/add", methods=['POST'])  # hcy#zzm修改
def add_customer_info(customerID):
    nickname = request.json['nickName']
    address = request.json['address']
    phone_number = request.json['phoneNumber']

    add_customer_info = """
    INSERT
    INTO info_customer(customer_id, address_name, nickname, phone)
    VALUES(:customer_id, :address_name, :nickname, :phone)
    """
    _ = run_sql(add_customer_info, {"customer_id": customerID,
                                    "address_name": address,
                                    "nickname": nickname,
                                    "phone": phone_number})
    d = {}
    return wrap_json_for_send(d, "successful")


# /api/customer/"id"/address/delete[已测试]
# input: base,{"customerID","address"}
# output: base
@customer.route("/<customerID>/address/delete", methods = ['POST','GET'])  # hcy#zzm修改
def delete_customer_info(customerID):
    address = request.json['address']
    delete_customer_info = """
    DELETE
    FROM info_customer
    WHERE customer_id=:customer_id AND address_name=:address_name
    """
    _ = run_sql(delete_customer_info, {"customer_id": customerID,
                                       "address_name": address})
    d = {}
    return wrap_json_for_send(d, "successful")


# /api/customer/"id"/address/update[已测试]
# input: base, {"customerID","nickName","phoneNumber","address"}
# ouput: base
@customer.route("/<customerID>/address/update", methods=['POST'])  # hcy　#　zzm修改
def update_customer_info(customerID):
    nickname = request.json['nickName']
    address = request.json['address']
    phone_number = request.json['phoneNumber']
    update_customer_info = """
    UPDATE info_customer
    SET nickname=:nickname, phone=:phone
    WHERE customer_id=:customer_id AND address_name=:address_name
    """
    _ = run_sql(update_customer_info, {"address_name": address,
                                       "nickname": nickname,
                                       "phone": phone_number,
                                       "customer_id": customerID})
    d = {}
    return wrap_json_for_send(d, "successful")


# 2. 用户购物车查询
# /api/customer/"id"/shoppingCart[已测试]
# input: base,"ID"
# output: base,{"totalSize","address":[{"address_name", "nickname", "phone"}] ,"cart_detail":[{"productID","pic_url",”count“,"productName","price"},...,{...}]}
@customer.route("/<id>/shoppingCart", methods = ['POST', 'GET'])  # hcy lsy(address)
def select_cart(id):
    select_cart = """
    SELECT p.product_id, pic_url, count, product_name, price, size
    FROM product p, cart c
    WHERE p.product_id = c.product_id AND c.customer_id=:customer_id
    """
    t_cart = run_sql(select_cart, {"customer_id": id})
    column_cart = ["productID", "picUrl", "count", "productName", "price", "size"]
    cart_list = [dict(zip(column_cart, t_cart[i].values())) for i in range(len(t_cart))]

    get_address = """
    SELECT address_name, nickname, phone FROM info_customer
    WHERE customer_id=:customer_id
    """
    t_address = run_sql(get_address, {"customer_id": id})
    column_address = ["addressName", "nickname", "phone"]
    address_info = [dict(zip(column_address, t_address[i].values())) for i in range(len(t_address))]
    d = {"totalSize": len(t_cart), "cartDetail": cart_list, "address": address_info}
    return wrap_json_for_send(d, 'successful')


# 在购物车界面只能增加某件商品的数量(update)，在商品界面才可以向购物车增加新的商品(add)
# /api/customer/"id"/shoppingCart/add【已测试】
# input: base,{"productID":,"count":3}
# output:base
# 例子
# {
# "productID": "xx"
# "count": 3
# }
# trigger的创建必须作为批处理中唯一的语句
@customer.route("/<id>/shoppingCart/add", methods=['POST'])  # hcy
def add_cart(id):
    product_id = request.json['productID']
    count = request.json['count']

    add_cart = """
    INSERT
    INTO cart(customer_id, product_id, count)
    VALUES(:customer_id, :product_id, :count)
    """

    run_sql(add_cart, {"customer_id": id, "product_id": product_id, "count": count})
    d = {}
    return wrap_json_for_send(d, 'successful')


# /api/customer/id/shoppingCart/update  仅限更新数量[已测试]
# input:base, {"count": "xxx", "productID":}
# output:base
@customer.route("/<id>/shoppingCart/update", methods=['POST'])  # hcy
def update_cart(id):
    product_id = request.json['productID']
    count = request.json['count']
    update_cart = """
    UPDATE cart
    SET count=:count
    WHERE customer_id=:customer_id AND product_id=:product_id
    """
    run_sql(update_cart, {"count": count,
                          "customer_id": id,
                          "product_id": product_id})
    d = {}
    return wrap_json_for_send(d, 'successful')


# /api/customer/id/shoppingCart/delete  删除购买的这一整个商品[已测试]
# input: base,{"customerID": "xxx", "productID":[列表！！！]}
# output: base
# 下订单后，删除购物车中购买的商品
@customer.route("/<id>/shoppingCart/delete", methods=['POST'])  # hcy
def delete_cart(id):
    product_id = request.json['productID']
    for i in product_id:
        delete_cart = """
        DELETE
        FROM cart
        WHERE customer_id=:customer_id AND product_id=:product_id
        """
        run_sql(delete_cart, {"customer_id": id,
                              "product_id": i})
    d = {}
    return wrap_json_for_send(d, 'successful')


# 3. 用户已有订单查询。返回用户已有订单。允许顾客进行退货处理。[已测试]
@customer.route("/<id>/orders", methods = ['POST', 'GET'])  # lsy
def get_orders(id):
    ## 提取信息
    get_orders = """
    SELECT o.order_id, o.orderdate, p.product_name, p.pic_url, o.quantity, o.price_sum, o.receive_address, i.phone, i.nickname, o.comment, o.is_return
    FROM product p, orders o, info_customer i
    WHERE o.customer_id=:customer_id 
    AND p.product_id = o.product_id AND o.customer_id = i.customer_id 
    AND o.receive_address = i.address_name;
    """
    t = run_sql(get_orders, {"customer_id": id})
    column = ['orderID', 'orderdate', 'productName', 'picUrl', 'quantity', 'priceSum', 'receiveAddress', 'phone', 'nickname',
              'comment', 'isReturn']
    d = [dict(zip(column, t[i].values())) for i in range(len(t))]
    d = {"number": len(t), "detail": d}
    return wrap_json_for_send(d, "successful")


@customer.route("/<id>/orders/salesreturn", methods=['POST'])  # lsy 【已测试】
def set_is_return(id):  # 设置退货标记
    order_id = request.json["orderID"]
    set_is_return = """
    UPDATE orders
    SET is_return = 1 
    WHERE order_id=:order_id;
    """
    t = run_sql(set_is_return, {"order_id": order_id})
    d = {}
    return wrap_json_for_send(d, "successful")


# 从购物车里添加新订单。[已测试]
# /api/customer/<id>/orders/add_cart
# input:base, {"orders": [" "productID", "order_date","price_sum", "quantity", "size","receive_address""]}
# output:base,{"orderID":["xxx", "xxx", "xxx"]}
# {version:0.1, statuscode:successful, orders: [{"productID","orderDate","priceSum","quantity","receiveAddress"}]}
@customer.route("/<id>/orders/add_cart", methods=['POST', 'GET'])  # zzm # hcy增加批量提交订单
def orders_add_cart(id):  # 新订单添加
    orders = request.json["orders"]
    orderID = []
    for i in range(len(orders)):
        product_id = orders[i]["productID"]
        order_date = orders[i]["orderDate"]
        price_sum = orders[i]["priceSum"]
        quantity = orders[i]["quantity"]
        # supplierID、deliverAddress 需后端查询得到_____finished by lsy
        # deliver_address = request.json["deliverAddress"]
        receive_address = orders[i]["receiveAddress"]
        get_need = """
        SELECT ifs.supplier_id, ifs.address_name
        FROM product p, info_supplier ifs
        WHERE p.product_id=:product_id AND p.supplier_id = ifs.supplier_id;  
        """
        need_info = run_sql(get_need, {"product_id": product_id})
        supplier_id = need_info[0]['supplier_id']
        deliver_address = need_info[0]['address_name']

        getNum = """
        SELECT COUNT(*) as cnt
        from orders  
         """
        tuple_tmp = run_sql(getNum)
        order_id_new = 'O' + str(int(tuple_tmp[0]['cnt'] + 1)).zfill(9)  # 获得新的订单编号

        orders_add = """
        INSERT
        INTO orders
        VALUES(:order_id, :customer_id, :supplier_id, :product_id, :orderdate, 
        :price_sum, :quantity, :deliver_address, :receive_address, :is_return, :comment)
        """

        run_sql(orders_add, {"order_id": order_id_new,
                             "customer_id": id,
                             "supplier_id": supplier_id,
                             "product_id": product_id,
                             "orderdate": order_date,
                             "quantity": quantity,
                             "price_sum": price_sum,
                             "deliver_address": deliver_address,
                             "receive_address": receive_address,
                             "is_return": 0,
                             "comment": ""})
        orderID.append(order_id_new)

    new_order_info = {"orderID": orderID}

    return wrap_json_for_send(new_order_info, "successful")


# 从商品界面里添加新订单。除接口外，与购物车添加订单均相同。（从商品界面一次只可以订购一种商品，无批量操作）[已测试]
# /api/customer/<id>/orders/add_product
#  input:base,{"productID","orderDate","priceSum","quantity",“size”,"receiveAddress"}
#  output:base, {"ordersID"}
#
# eg.
# {
#     "productID": "P000000001",
#     "orderDate": "2020-07-14 11:21:08",
#     "priceSum": "1000",
#     "quantity": "5",
#     "receiveAddress": "somewhere1234"
# }

# output:{"ordersID":"O1234"}

@customer.route("/<id>/orders/add_product", methods=['POST', 'GET'])  # zzm #hcy
def orders_add_product(id):  # 新订单添加

    product_id = request.json['productID']
    order_date = request.json['orderDate']
    price_sum = request.json['priceSum']
    quantity = request.json['quantity']
    receive_address = request.json['receiveAddress']

    getNum = """
    SELECT COUNT(*) as cnt
    from orders  
    """

    tuple_tmp = run_sql(getNum)
    order_id_new = 'O' + str(int(tuple_tmp[0]['cnt'] + 1)).zfill(9)  # 获得新的订单编号

    getInfo = """
    SELECT info_s.address_name da, s.supplier_id sid
    FROM product p,supplier s, info_supplier info_s
    WHERE p.product_id=:product_id AND p.supplier_id=s.supplier_id
          AND s.supplier_id=info_s.supplier_id

    """
    t = run_sql(getInfo, {"product_id": product_id})
    deliver_address = t[0]['da']
    supplier_id = t[0]['sid']

    orders_add = """
    INSERT
    INTO orders
    VALUES(:order_id, :customer_id, :supplier_id, :product_id, :orderdate, 
    :price_sum, :quantity, :deliver_address, :receive_address, :is_return, :comment)
    """

    run_sql(orders_add, {"order_id": order_id_new,
                         "customer_id": id,
                         "supplier_id": supplier_id,
                         "product_id": product_id,
                         "orderdate": order_date,
                         "quantity": quantity,
                         "price_sum": price_sum,
                         "deliver_address": deliver_address,
                         "receive_address": receive_address,
                         "is_return": 0,
                         "comment": ""})

    new_order_info = {"ID": order_id_new}

    return wrap_json_for_send(new_order_info, "successful")


# 显示此顾客所有的收货地址以供选择
# /api/customer/<id>/orders/get_address
# input:base,{""}
# output:base, {"address_name", "nickname", "phone"}
#
@customer.route("/<id>/orders/get_address", methods = ['POST', 'GET'])  # lsy【zzm已测试】
def orders_get_address(id):  # 显示所有地址
    get_address = """
    SELECT address_name, nickname, phone 
    FROM info_customer
    WHERE customer_id=:customer_id
    """
    t = run_sql(get_address, {"customer_id": id})
    column = ["addressName", "nickname", "phone"]
    address_info = [dict(zip(column, t[i].values())) for i in range(len(t))]
    d = {"addressInfo": address_info}
    return wrap_json_for_send(d, 'successful')
