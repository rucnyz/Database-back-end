from flask import Blueprint, request

from utils import run_sql, wrap_json_for_send

comment = Blueprint('comment', __name__)


# 4. 评价功能：与顾客订单进行绑定。当订单交易完成后，顾客可以选择对商品进行评价，并存储在数据库中。
# count
@comment.route("/", methods=['POST'])  # lsy
def select_comments():  # 查看评价
    product_id = request.json["product_id"]
    select_comments = """
    SELECT product_id, customer_id, comment
    FROM orders o 
    WHERE product_id = '%s' ; 
    """ % product_id
    tuple = run_sql(select_comments)
    column = ['productID', 'ctName', 'quantity']
    d = [dict(zip(column, tuple[i].values())) for i in range(len(tuple))]
    t = {"number": len(tuple), "detail": d}
    return wrap_json_for_send(t, "successful")

# add和delete都不需要了，直接update
# @comment.route("/add", methods=['POST'])  # lsy
# def add_comment():  # 添加评价
#     order_id = request.json["order_id"]
#     comment = request.json["comment"]
#     add_comment = """
#     UPDATE orders
#     SET comment = '%s'
#     WHERE order_id = '%s';
#     """ % (comment, order_id)
#     t = run_sql(add_comment)
#     d = {}
#     return wrap_json_for_send(d, "successful")
#
#
# @comment.route("/delete", methods=['POST'])  # lsy
# def delete_comment():  # 删除评价
#     order_id = request.json["order_id"]
#     delete_comment = """
#     UPDATE orders
#     SET comment = NULL
#     WHERE order_id = '%s';
#     """ % order_id
#     t = run_sql(delete_comment)
#     d = {}
#     return wrap_json_for_send(d, "successful")


# /api/comments/update[后端已完成]
# input: base, {"orderID“,"comment"}
# output: base
@comment.route("/update", methods=['POST'])  # lsy
def update_comment():  # 更新评价
    order_id = request.json["order_id"]
    comments = request.json["comment"]

    update_comment = """
    UPDATE orders
    SET comment = '%s'
    WHERE order_id = '%s';
    """ % (comments, order_id)
    t = run_sql(update_comment)
    d = {}
    return wrap_json_for_send(d, "successful")
