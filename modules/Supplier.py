from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

supplier = Blueprint('supplier', __name__)
db = SQLAlchemy()


# 商家进行注册,利用所有人的身份证进行登录
# /api/supplier/register
# input:base, { "password", "supplierName", "ownerName", "ownerID"}
# output: base, {”supplier_id“}

@supplier.route("/register", methods=['POST', 'GET'])  # zzm
def register():
    password = request.json['password'][:10]
    supplier_name = request.json['supplierName']
    owner_name = request.json['ownerName']
    owner_id = request.json['ownerID']
    message = None

    getNum = """
     SELECT COUNT(*) as cnt
    from supplier   
     """
    tuple_tmp = run_sql(getNum)
    supplier_id_new = 'S' + str(int(tuple_tmp[0]['cnt'])+1).zfill(9)

    register = """
    INSERT 
    INTO supplier
    VALUES(:supplier_id_new, :password, :supplier_name, :owner_name, :owner_id)
    """
    try:
        _ =run_sql(register,{"supplier_id_new": supplier_id_new,
                             "password": password,
                             "supplier_name": supplier_name,
                             "owner_name": owner_name,
                             "owner_id": owner_id})
        statuscode = 'successful'
        new_supp_info = {"ID": supplier_id_new}
    except:
        statuscode = "failed"
        message = "注册失败，该账户已被注册！"
        new_supp_info = {}
    return wrap_json_for_send(new_supp_info, statuscode, message = message)


# 商家登录。用户提供登录名与密码，与数据库中内容进行匹配验证，返回登录成功与否。
# /api/supplier/login
# input: base, {"ownerID":"xxx","password:"xxx"}
# output: base, {"suppID":"xxx"}
@supplier.route("/login", methods=['POST', 'GET'])  # zzm
def login():
    owner_id = request.json['ownerID']
    password = request.json['password'][:10]
    check_regi = """
    SELECT supplier_id
    FROM supplier
    WHERE owner_id=:owner_id
    """
    message = None
    t = run_sql(check_regi,{"owner_id":owner_id})
    if(len(t) == 0):
        out = {}
        statuscode = "failed"
        message = "用户尚未注册!"
    else:
        login = """
         SELECT supplier_id
         FROM supplier
         WHERE owner_id=:owner_id AND supplier_password=:supplier_password
         """
        t = run_sql(login,{"owner_id":owner_id,
                           "supplier_password":password})
        if (len(t) == 0):
            out = {}
            statuscode = "failed"
            message = "用户名或密码错误！"
        else:
            supplier_id = t[0]['supplier_id']
            info = """
                SELECT supplier_name suppname
                FROM supplier
                WHERE supplier_id=:supplier_id
                """
            s_info = run_sql(info,{"supplier_id":supplier_id})
            suppname =s_info[0]['suppname']
            out = {"suppID":supplier_id}
            statuscode = "successful"



    return wrap_json_for_send(out,statuscode , message = message )


# 应该为return wrap_json_for_send(supp_ID, "successful")

# 商家界面-lsy
# 1. 店铺展示商家主要出售的产品，售货量以及库存。
# /api/supplier/"id"/homepage
# input:
# output:
@supplier.route("/<id>/homepage", methods=['POST', 'GET'])  # lsy
def get_homepage(id):
    supplier_id = id
    # tuple = run_sql(login)
    # supp_ID = [{"ID": tuple[0]}]
    get_homepage = """
    SELECT DISTINCT p.product_id, product_name, price, pic_url, ISNULL(sub.sales, 0)
    FROM product p 
    LEFT JOIN(
        SELECT orders.product_id, sum(orders.quantity) sales
        FROM product, orders
        WHERE product.product_id=orders.product_id 
        GROUP BY orders.product_id
        ) sub
        ON p.product_id=sub.product_id
    WHERE p.supplier_id=:supplier_id  AND remain >0 
    ORDER BY p.product_id;
    """
    t = run_sql(get_homepage,{"supplier_id":supplier_id})
    column = ["商品ID", "商品名称", "商品价格", "商品图片", "商品销量"]

    list = [dict(zip(column, t[i].values())) for i in range(len(t))]
    d = {"details": list}

    return wrap_json_for_send(d, 'successful')


# 2. 已有订单管理。返回以商品and以日期为组的全部订单。两种排序方式。-以时间为组
# /api/supplier/"id"/orders
# output: base, {detail:[{下单时间：time，顾客id：id，商品名称：name，商品数量：quantity，订单总额:sumprice}]}
@supplier.route("/<id>/orders", methods=['POST', 'GET'])  # lsy
def get_orders(id):
    # tuple = run_sql(login)
    # supp_ID = [{"ID": tuple[0]}]
    get_orders = """
    SELECT o.orderdate, o.customer_id, p.product_name, o.quantity,  sum(price_sum) sum_price
    FROM orders o, product p
    WHERE o.supplier_id=:supplier_id AND o.product_id=p.product_id
    GROUP BY o.orderdate, o.customer_id, p.product_name, o.quantity
    ORDER BY orderdate, customer_id;
    """
    ## count 是一共购买了多少件商品。每个商品又可能买了很多件(quantity),但在这一页面不展示。
    # 以上是不建立视图的情况
    # 若建立视图，则为：
    # get_orders = """
    #    SELECT orderdate, customer_id, sum(price_sum) sum_price,
    #    count(*) count, deliver_address, receive_address
    #    FROM sum_orders
    #    WHERE supplier_id = '%s'
    #    GROUP BY orderdate, customer_id, deliver_address, receive_address
    #    """ % id
    t = run_sql(get_orders, {"supplier_id": id})
    column = ["下单时间", "顾客ID","商品名称", "商品数量", "订单总额"]
    d = {"detail": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    return wrap_json_for_send(d, "successful")


# 3. 已有订单明细查询管理。返回上一步查到的订单里的全部商品
# /api/supplier/"id"/orders/items
# input:base,{"orderdate", "customer_id"}
# output:base,{"product_id", "product_name","price_sum", "quantity"}
@supplier.route("/<id>/orders/items", methods=['POST', 'GET'])  # lsy
def get_order_items(id):
    time = request.json['orderdate']
    customer_id = register.json['customer_id']
    get_items = """
    SELECT o.product_id, p.product_name, o.price_sum, o.quantity
    FROM orders o, product p
    WHERE o.supplier_id=:supplier_id AND o.orderdate=orderdate AND o.customer_id=customer_id
        AND o.product_id=p.product_id;
    """
    t = run_sql(get_items,{"supplier_id":id,
                           "orderdate":time,
                           "customer_id":customer_id})
    column = ["商品id", "商品名称", "商品总价", "商品数量"]
    d = {"detail": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    return wrap_json_for_send(d, "successful")


# 4. 增加一个新商品。
# /api/supplier/"id"/product/add
# input:base,{"product_name","price","remain","size","discount","category",pic_url"}
# output:base,{"product_id"}

@supplier.route("/<id>/product/add", methods=['POST', 'GET'])  # lsy
def add_product(id):
    product_name = request.json['product_name']
    price = request.json['price']
    remain = request.json['remain']
    size = request.json['size']
    discount = request.json['discount']
    category = request.json['category']
    pic_url = request.json['pic_url']
    getNum = """
    SELECT COUNT(*) as cnt
    FROM product;
    """
    num = run_sql(getNum)
    product_id_new = 'P' + str(int(num['cnt'][0])+1).zfill(9)
    add_product = """
    INSERT 
    INTO product
    VALUES(:product_id_new, :product_name, :price, :id, :remain, :size, :discount, :category, :pic_url)
    """
    _ = run_sql(add_product,{"product_id_new": product_id_new,
                             "product_name": product_name,
                             "price":price,
                             "id":id,
                             "remain":remain,
                             "size":size,
                             "discount":discount,
                             "category":category,
                             "pic_url":pic_url})

    d = {"ID": product_id_new}
    return wrap_json_for_send(d, "successful")


# 5. 删除商品。
# /api/supplier/"id"/product/delete
# input:base,{"product_id"}
# output:base,{""}
@supplier.route("/<id>/product/delete", methods=['POST', 'GET'])  # lsy
def delete_product(id):
    supplier_id = id
    product_id = request.json['product_id']
    delete_product = """
    DELETE
    FROM product
    WHERE product_id=:product_id AND supplier_id=:supplier_id
    """
    run_sql(delete_product,{"product_id":product_id,
                            "supplier_id":supplier_id})
    d = {}
    return wrap_json_for_send(d, "successful")


# 6. 修改商品。
# /api/supplier/"id"/products/update
# input:base,{"product_id","product_name","price","remain","size","discount","category",pic_url"}
# output:base,{""}
@supplier.route("/<id>/products/update", methods=['POST', 'GET'])  # lsy
def update_product(id):
    supplier_id = id
    product_id = request.json['product_id']
    product_name = request.json['product_name']
    price = request.json['price']
    remain = request.json['remain']
    size = request.json['size']
    discount = request.json['discount']
    category = request.json['category']
    pic_url = request.json['pic_url']

    update_product = """
    UPDATE product
    SET product_name = '%s', price = %u, remain = %u, size = '%s', discount = %f,category = '%s', pic_url = '%s'
    WHERE product_id = '%s' AND supplier_id = '%s'
    """ % (product_name, price, remain, size, discount, category, pic_url, product_id, supplier_id)
    _ = run_sql(update_product,{"product_name":product_name,
                                "price":price,
                                "remain":remain,
                                "size":size,
                                "discount":discount,
                                "category":category,
                                "pic_url":pic_url,
                                "product_id":product_id,
                                "supplier_id":supplier_id})
    d = {}
    return wrap_json_for_send(d, "successful")
