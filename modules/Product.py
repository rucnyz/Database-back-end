from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

product = Blueprint('product', __name__)

db = SQLAlchemy()


# /api/product/"商品ID"【已测试】
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
@product.route("/<id>", methods = ['POST', 'GET'])  # hcy
def product_info(id):
    product_info = """
    SELECT s.supplier_name, ifs.address_name, product_name, price, remain, size, category, pic_url
    FROM product p, supplier s, info_supplier ifs
    WHERE product_id=:product_id AND s.supplier_id=p.supplier_id AND ifs.supplier_id=p.supplier_id
    """
    t = run_sql(product_info, {"product_id": id})

    d = {
        "supplierName": t[0]['supplier_name'],
        "supplierAddress": t[0]['address_name'],
        "productName": t[0]['product_name'],
        "price": t[0]['price'],
        "remain": t[0]['remain'],
        "size": t[0]['size'],
        "category": t[0]['category'],
        "pic_url": t[0]['pic_url']
    }
    return wrap_json_for_send(d, 'successful')


# /api/product/“商品ID"/allcomments【已测试】
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
#       'comment': '情况注册全部增加能力积分对于.'
#       'date': "xxx"
#       'customerID': "xxx"
#     }
#   ]
# }

@product.route("/<productID>/allcomments", methods = ['POST', 'GET'])  # hcy #zzm修改 【已测试】
def allcomments(productID):
    need_number = request.args['needNumber']
    page = request.args['page']
    out_num = (int(page) - 1) * int(need_number)
    total = """
    SELECT count(*) cnt
    FROM orders o 
    WHERE o.product_id=:productID AND o.comment!=''
    """
    comment = """
        SELECT TOP %s o.comment, o.orderdate, c.customer_nickname
        FROM orders o, customer c
        WHERE o.product_id=:productID AND c.customer_id=o.customer_id AND o.comment!=''
            AND order_id NOT IN ( SELECT TOP %s o.order_id
                                  FROM orders o, customer c
                                  WHERE o.product_id=:productID AND c.customer_id=o.customer_id)
    """ % (need_number, out_num)
    # 数字直接传，不涉及安全，id放在run_sql里传
    total_size = run_sql(total, {"productID": productID})
    c = run_sql(comment, {"productID": productID})
    column = ["comments", "date", "nickname"]
    d = {"totalSize": total_size[0]['cnt'], "comments": [dict(zip(column, c[i].values())) for i in range(len(c))]}

    return wrap_json_for_send(d, 'successful')
