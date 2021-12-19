from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

product = Blueprint('product', __name__)

db = SQLAlchemy()


# /api/product/"商品ID"
# input: base, {"ID"}
# output: base, {"productName", "price", "remain", "size", "category", "pic_url", "comment":[{'comment'}]}
# input例子
# {
# "productID":'xx'
# }
# output例子
# {
#   'supplierName': "xxx"
#   'supplierAddress': "发货地址"
#   'productName': '悠享时YOTIME-年货大礼包曲奇饼干礼盒',
#   'price': 189,
#   'remain': 16,
#   'size': 'M',
#   'category': '配饰',
#   'pic_url': 'https://img14.360buyimg.com/n7/jfs/t1/168641/4/25410/143878/61a864c4E342d985c/5daf74ceca47577e.jpg',
# }
@product.route("/<id>", methods = ['POST'])  # hcy#张子木修改
def product_info(id):
    product_id = request.json['productID']
    product_info = """
    SELECT product_name, price, remain, size, category, pic_url
    FROM product
    WHERE product_id='%s'
    """ % id
    t = run_sql(product_info)

    comment = """
    SELECT TOP 5 comment
    FROM orders
    WHERE product_id='%s'
    """ % id
    c = run_sql(comment)

    d = {"productName": t[0]['product_name'],
         "price": t[0]['price'],
         "remain": t[0]['remain'],
         "size": t[0]['size'],
         "category": t[0]['category'],
         "pic_url": t[0]['pic_url'],
         "comments": c}
    return wrap_json_for_send(d, 'successful')


# /api/product/“商品ID"/allcomments
# input: base, {"ID"}
# output:base, {"comments":[]}
# iput例子
# {
# 'productID': 'xxxx'
# 'needNumber': 20
#   'page': 1
#
# }
# output例子
# {
#   'comments': [
#     {
#       'customerID': "xxx"
#       'comment': '情况注册全部增加能力积分对于.'
#     }
#   ]
# }

@product.route("/<id>/allcomments", methods = ['POST'])  # hcy #zzm修改
def allcomments(id):
    need_number = request.json['needNumber']
    page = request.json['page']

    comment = """
    SELECT TOP %s comment
    FROM orders
    WHERE product_id='%s'
    """ %(need_number,id)
    c = run_sql(comment)

    d = {"comments": c}
    return wrap_json_for_send(d, 'successful')