from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

comment = Blueprint('comment', __name__)

db = SQLAlchemy()


# 4. 评价功能：与顾客订单进行绑定。当订单交易完成后，顾客可以选择对商品进行评价，并存储在数据库中。
# count
@comment.route("/", methods = ['POST'])  # lsy
def select_comments():  # 查看评价
    product_id = request.args["product_id"]
    select_comments = """
    SELECT product_id, customer_id, comment
    FROM orders o 
    WHERE product_id = %s ; 
    """ % product_id
    tuple = run_sql(select_comments, db)
    column = ['productID', 'ctName', 'quantity']
    d = [dict(zip(column, tuple[i])) for i in range(len(tuple))]
    t = {"number": len(tuple), "detail": d}
    return wrap_json_for_send(t, "successful")


@comment.route("/add", methods = ['POST'])  # lsy
def add_comment():  # 添加评价
    order_id = request.args["order_id"]
    comment = request.args["comment"]
    add_comment = """
    UPDATE orders
    SET comment = %s
    WHERE order_id = %s;
    """ % (comment, order_id)
    t = run_sql(add_comment, db)
    # TODO
    d = {}
    return wrap_json_for_send(d, "successful")


@comment.route("/delete", methods = ['POST'])  # lsy
def delete_comment():  # 删除评价
    order_id = request.args["order_id"]
    delete_comment = """
    UPDATE orders
    SET comment = NULL
    WHERE order_id = %s;
    """ % order_id
    t = run_sql(delete_comment, db)
    # TODO
    d = {}
    return wrap_json_for_send(d, "successful")


@comment.route("/update", methods = ['POST'])  # lsy
def update_comment():  # 更新评价
    order_id = request.args["order_id"]
    comment = request.args["comment"]
    update_comment = """
    UPDATE orders
    SET comment = %s
    WHERE order_id = %s;
    """ % (comment, order_id)
    t = run_sql(update_comment, db)
    # TODO
    d = {}
    return wrap_json_for_send(d, "successful")
