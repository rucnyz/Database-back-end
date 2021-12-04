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
# 应该为return wrap_json_for_send(new_supp_info, "successful")

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
# 应该为return wrap_json_for_send(supp_ID, "successful")

# 商家界面-lsy
# 1. 店铺展示商家主要出售的产品，售货量以及库存。
# /api/supplier/"id"/homepage
# input:
# output:
@supplier.route("/<id>/homepage", methods=['POST', 'GET'])  # lsy
def get_homepage(id):
    supplier_id = id
    # tuple = run_sql(login, db)
    # supp_ID = [{"ID": tuple[0]}]
    get_homepage = """
    SELECT DISTINCT p.product_id, product_name, price, pic_url, ISNULL(sub.sales, 0) sales
    FROM product p
    LEFT JOIN(
        SELECT product.product_id, count(*) sales
        FROM product, orders
        WHERE product.product_id = orders.product_id 
        GROUP BY product_id
        ) sub
        ON p.product_id = sub.product_id
    WHERE p.supplier_id = %s  AND remain >0 
    ORDER BY p.product_id
    """ % supplier_id
    tuple = run_sql(get_homepage, db)
    sales =
    column = ["商品ID", "商品名称", "商品价格", "商品图片", "商品销量"]
    d = [dict(zip(column,tuple[i])) for i in range(len(tuple))]
    return wrap_json_for_send(d, "successful")

# 2. 已有订单管理。返回以商品and以日期为组的全部订单。两种排序方式。-以时间为组
# /api/supplier/"id"/orders
@supplier.route("/<id>/orders", methods=['POST', 'GET'])  # lsy
def get_orders(id):
    # tuple = run_sql(login, db)
    # supp_ID = [{"ID": tuple[0]}]
    get_orders = """
    SELECT orderdate, customer_id, sum(price_sum) sum_price, 
    count(*) count, deliver_address, receive_address
    FROM orders
    WHERE supplier_id = %s 
    GROUP BY orderdate, customer_id, deliver_address, receive_address
    ORDER BY orderdate, customer_id
    """ % id
    ## count 是一共购买了多少件商品。每个商品又可能买了很多件(quantity),但在这一页面不展示。
    # 以上是不建立视图的情况
    # 若建立视图，则为：
    # get_orders = """
    #    SELECT orderdate, customer_id, sum(price_sum) sum_price,
    #    count(*) count, deliver_address, receive_address
    #    FROM sum_orders
    #    WHERE supplier_id = %s
    #    GROUP BY orderdate, customer_id, deliver_address, receive_address
    #    """ % id
    tuple = run_sql(get_orders, db)
    column = ["下单时间", "顾客名称", "订单总额", "商品数量", "发货地址", "收货地址"]
    d = [dict(zip(column,tuple[i])) for i in range(len(tuple))]
    return wrap_json_for_send(d, "successful")

# 3. 已有订单明细查询管理。返回上一步查到的订单里的全部商品
# /api/supplier/"id"/orders/items
# input:base,{"orderdate", "customer_id"}
# output:base,{"product_id", "product_name","price_sum", "quantity"}
@supplier.route("/<id>/orders/items", methods=['POST', 'GET'])  # lsy
def get_order_items(id):
    time = request.args['orderdate']
    customer_id =register.args['customer_id']
    get_items = """
    SELECT o.product_id, p.product_name, o.price_sum, o.quantity
    FROM orders, product
    WHERE o.supplier_id = %s AND o.orderdate = %s AND o.customer_id = %s
        AND o.product_id = p.product_id
    """ % (id, time, customer_id)
    tuple = run_sql(get_items, db)
    column = ["商品id", "商品名称", "商品总价", "商品数量"]
    d = [dict(zip(column,tuple[i])) for i in range(len(tuple))]
    return wrap_json_for_send(d, "successful")


# 4. 增加一个新商品。
# /api/supplier/"id"/product/add
# input:base,{"product_name","price","remain","size","discount","category",pic_url"}
# output:base,{"product_id"}

@supplier.route("/<id>/homepage", methods=['POST', 'GET'])  # lsy
def add_product(id):
    product_name = request.args['product_name']
    price = request.args['price']
    remain = request.args['remain']
    size = request.args['size']
    discount = request.args['discount']
    category = request.args['category']
    pic_url = request.args['pic_url']
    getNum = """
    SELECT COUNT(*)
    FROM product  
    """
    tuple = run_sql(getNum,db)
    product_id_new = 'P' + tuple[0]
    add_product = """
    INSERT 
    INTO product
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """ % (product_id_new, product_name, price, id, remain, size, discount, category, pic_url)
    tuple = run_sql(get_homepage, db)
    d = [{"ID": product_id_new}]
    return wrap_json_for_send(d, "successful")

# 5. 删除商品。
# /api/supplier/"id"/product/delete
# input:base,{"product_id"}
# output:base,{""}
@supplier.route("/<id>/product/delete", methods=['POST', 'GET'])  # lsy
def login(id):
    supplier_id = id
    product_id = request.args['product_id']
    delete_product = """
    DELETE
    FROM product
    WHERE product_id = %s AND supplier_id = %s
    """ % (product_id, supplier_id)
    tuple = run_sql(delete_product, db)
    d = {}
    return wrap_json_for_send(d, "successful")

# 6. 修改商品。
# /api/supplier/"id"/products/update
# input:base,{"product_id","product_name","price","remain","size","discount","category",pic_url"}
# output:base,{""}
@supplier.route("/<id>/products/update", methods=['POST', 'GET'])  # lsy
def update_product(id):
    supplier_id = id
    product_id = request.args['product_id']
    product_name = request.args['product_name']
    price = request.args['price']
    remain = request.args['remain']
    size = request.args['size']
    discount = request.args['discount']
    category = request.args['category']
    pic_url = request.args['pic_url']
    update_product = """
    UPDATE product
    SET product_name = %s, price = %s, remain = %s, size = %s, discount = %s,category = %s, pic_url = %s
    WHERE product_id = %s AND supplier_id = %s
    """ % (product_name,price, remain, size, discount, category, pic_url, product_id, supplier_id)
    tuple = run_sql(update_product, db)
    d={}
    return wrap_json_for_send(d, "successful")