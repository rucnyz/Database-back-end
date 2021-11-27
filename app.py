from flask import Flask,request
from json import load
from json import dumps

from flask_sqlalchemy import SQLAlchemy
from flask import request


# 初始化app
app = Flask(__name__)

app.config.from_file("./mssql_config.json", load=load)
# 连接数据库
db = SQLAlchemy(app)

# SQLALCHEMY_DATABASE_URI

# 用于连接数据的数据库。

# SQLALCHEMY_TRACK_MODIFICATIONS

# 如果设置成 True (默认情况)，
# Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
# 这需要额外的内存， 如果不必要的可以禁用它。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


def run_sql(T_sql):  # 把T_sql放到sql server中运行
    cursor = db.engine.execute(T_sql)
    ret = cursor.fetchall()
    return ret


def wrap(d, status_code, version=0.1):
    d['version'] = version
    d['statusCode'] = status_code
    return dumps(d)


@app.route("/api/test", methods=['POST'])
def test():
    content = request.json
    print(content)
    return content


# 	a. 此处商品展示仅有缩略图与商品名。
# /api/getHomePage
# input:base, {"needNumber":xx（数字）}
# output: base, {{"商品id"：id，"商品图片"：图片url，"商品名称"：名称，"商品价格"：价格},{……},{……}}
@app.route("/api/getHomePage", methods=['POST', 'GET'])  # zzm
def get_homePage():
    number = request.args['needNumber']
    get_homePage = """
    SELECT TOP %s product_id, pic_url, product_name, price 
    FROM product p 
    ORDER BY NewID()
    """ % number

    tuple = run_sql(get_homePage)
    column = ["商品ID", "商品图片", "商品名称", "商品价格"]
    d = [dict(zip(column,tuple[i])) for i in range(len(tuple))]

    return dumps(d)


#  /api/getHomePage/category（固定栏）
# input: base
# output: base ,{"number":xx（数字）,"分类”:[……, ……,……]}
@app.route("/api/getHomePageCategory", methods=['POST', 'GET'])  # zzm
def get_homepage_category():
    get_homepage_category = """
    select p.category UNIQUE
    from product p       
    """

    tuple = run_sql(get_homepage_category)[0]
    d = {"number": len(tuple), "分类": tuple}

    return dumps(d)


# 用户注册功能。用户提供个人信息（姓名、电话号），设置昵称，利用手机号注册，设置密码，在数据库中生成会员ID。昵称允许重复。注册成功则跳转登录界面。注册失败反馈。
# /api/register
# input: base, {"phoneNumber":"xxx", "password": "xxx"}
# output:base {"ID":"xxx"}
# 备注：密码生成方式：用户密码sha256取前20位

@app.route("/api/register", methods=['POST', 'GET'])  # zzm
def register():
    phone_number = request.args['phoneNumber']
    password = request.args['password']

    getNum = """
     SELECT COUNT*
    from cumtomer   
     """
    tuple = run_sql(getNum)
    customer_id_new = 'C' + tuple[0]

    register = """
    INSERT 
    INTO customer
    VALUES(%s, %s, %s)
    """ % (customer_id_new, phone_number, password)

    db.engine.execute(register)
    new_cust_info = [{"ID": customer_id_new}]

    return dumps(new_cust_info)


# 用户登录。用户提供登录名与密码，与数据库中内容进行匹配验证，返回登录成功与否。
# /api/login
# input: base, {"name":"xxx","password:"xxx"}
# output: base, {"ID":"xxx"}
@app.route("/api/login", methods=['POST', 'GET'])  # zzm
def login():
    name = request.args['name']
    password = request.args['password']
    login = """
    SELECT customer_id
    FROM custmer
    WHERE customer_name = %s AND customer_password = %s
    """ % (name, password)

    tuple = run_sql(login)
    cust_ID = [{"ID": tuple[0]}]

    return dumps(cust_ID)


# 用户个人信息查询
# /api/customer/ID:"xxx"/info
# input : base, {"ID":"xxx"}
# output: base, {"nickName":"xxx", "phoneNumber":"xxx","address":list(无则返回空); }
@app.route("/api/customer/<id>/info", methods=['POST'])  # hcy
def select_customer_info(id):
    # content = request.json
    select_customer_info = """
    SELECT nickname, phone, address_name
    FROM info_customer
    WHERE customer_id = %s
    """ % id
    tuple = run_sql(select_customer_info)
    column = ['nickName', 'phoneNumber', 'address']
    list = [dict(zip(column, tuple[i])) for i in range(len(tuple))]
    d = {"detail": list}
    return wrap(d, 'successful')


# /api/customer/"id"/address/add
# input:base,{"ID","nickName","address","phoneNumber"}
# output: base
@app.route("/api/customer/<id>/address/add", methods=['POST'])  # hcy
def add_customer_info(id):
    nickname = request.args['nickName']
    address = request.args['address']
    phone_number = request.args['phoneNumber']

    add_customer_info = """
    INSERT
    INTO info_customer(customer_id, address_name, nickname, phone)
    VALUES('%s', '%s', '%s', '%s')
    """ % (id, nickname, address, phone_number)
    run_sql(add_customer_info)

    return


# /api/customer/"id"/address/delete
# input: base,{"ID","address"}
# output: base
@app.route("/api/customer/<id>/address/delete", methods=['POST'])  # hcy
def delete_customer_info(id):
    address = request.args['address']
    delete_customer_info = """
    DELETE
    FROM info_customer
    WHERE customer_id = %s, address_name = %s
    """ % (id, address)
    run_sql(delete_customer_info)
    return


# /api/customer/"id"/address/update
# input: base, {"ID","nickName","phoneNumber","address"}
# ouput: base
@app.route("/api/customer/<id>/address/update", methods=['POST'])  # hcy
def update_customer_info(id):
    nickname = request.args['nickName']
    address = request.args['address']
    phone_number = request.args['phoneNumber']
    update_customer_info = """
    UPDATE info_customer
    SET address_name = %s, nickname = %s, phone = %s
    WHERE customer_id = %s
    """ % (nickname, address, phone_number, id)
    run_sql(update_customer_info)
    return


# 2. 用户购物车查询
# /api/customer/"id"/shoppingCart
# input: base,"ID"
# output: base,{"total number", "detail":[{"productID","pic_url",”count“,"productName"},...,{...}]}
@app.route("/api/customer/<id>/shoppingCart", methods=['POST'])  # hcy
def select_cart(id):
    select_cart = """
    SELECT p.product_id, pic_url, count, product_name
    FROM product p, cart c
    WHERE p.product_id = c.product_id AND c.customer_id = %s
    """ % id
    tuple = run_sql(select_cart)
    column = ["productID", "pic_url", "count", "productName"]
    list = [dict(zip(column, tuple[i])) for i in range(len(tuple))]
    d = {"total number": len(tuple), "detail": list}
    return wrap(d, 'successful')


# /api/customer/"id"/shoppingCart/add
# input: base,{"用户ID": "xxx", "商品ID":,"商品数量"}
# output:base
@app.route("/api/customer/<id>/shoppingCart", methods=['POST'])  # hcy
# @TODO: IF EXIST





# 3. 用户已有订单查询。返回用户已有订单。允许顾客进行退货处理。
@app.route("/api/customer/<id>/orders", methods=['POST'])  # lsy
def get_orders(id):
    content = request.json
    ## 提取信息
    get_orders = """
    SELECT order_id, p.product_id, product_name, quantity 
    FROM product p, orders o
    WHERE o.customer_id = %s 
    AND p.product_id = o.product_id;
    """ % id
    tuple = run_sql(get_orders)
    column = ['orderID','productID', 'productID', 'quantity']
    d = [dict(zip(column, tuple[i])) for i in range(len(tuple))]
    d = {"number": len(tuple), "detail": d}
    return wrap(d, "successful")


@app.route("/api/customer/<id>/orders/salesreturn", methods=['POST'])  # lsy
def set_is_return(id):  # 设置退货标记
    order_id = request.args["order_id"]
    set_is_return = """
    UPDATE orders
    SET is_return = 1 
    WHERE order_id = %s ;
    """ % order_id
    tuple = run_sql(get_orders)
    d = {}
    return wrap(d, "successful")


# 4. 评价功能：与顾客订单进行绑定。当订单交易完成后，顾客可以选择对商品进行评价，并存储在数据库中。
# count
@app.route("/api/comments", methods=['POST'])  # lsy
def select_comments():  # 查看评价
    product_id = request.args["product_id"]
    select_comments = """
    SELECT product_id, customer_id, comment
    FROM orders o 
    WHERE product_id = %s ; 
    """ % product_id
    tuple = run_sql(select_comments)
    column = ['productID', 'ctName', 'quantity']
    d = [dict(zip(column, tuple[i])) for i in range(len(tuple))]
    d = {"number": len(tuple), "detail": d}
    return wrap(d, "successful")


@app.route("/api/comments/add", methods=['POST'])  # lsy
def add_comment():  # 添加评价
    order_id = request.args["order_id"]
    comment = request.args["comment"]
    add_comment = """
    UPDATE orders
    SET comment = %s
    WHERE order_id = %s;
    """ % (comment, order_id)
    tuple = run_sql(add_comment)
    d = {}
    return wrap(d, "successful")


@app.route("/api/comments/delete", methods=['POST'])  # lsy
def delete_comment():  # 删除评价
    order_id = request.args["order_id"]
    delete_comment = """
    UPDATE orders
    SET comment = NULL
    WHERE order_id = %s;
    """ % order_id
    tuple = run_sql(delete_comment)
    d = {}
    return wrap(d, "successful")


@app.route("/api/comments/update", methods=['POST'])  # lsy
def update_comment():  # 更新评价
    order_id = request.args["order_id"]
    comment = request.args["comment"]
    update_comment = """
    UPDATE orders
    SET comment = %s
    WHERE order_id = %s;
    """ % (comment, order_id)
    tuple = run_sql(update_comment)
    d = {}
    return wrap(d, "successful")


@app.route("/", methods=['GET'])
def test_run():
    # cursor = db.engine.execute("select * from dbo.course")
    # ret = cursor.fetchone()
    return "hello"

if __name__ == "__main__":
    app.run(debug=True, port=5200, host="0.0.0.0")
