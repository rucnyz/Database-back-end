# -*- coding: utf-8 -*-
# @Time    : 2021/12/11 21:10
# @Author  : HCY
# @File    : Product.py
# @Software: PyCharm

from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

product = Blueprint('product', __name__)

# /api/products/"商品ID"
# input: base, {"ID"}
# output: base, {"productName", "price", "remain", "size", "category", "pic_url", "comment":[{'comment'}]}
@product.route("/<id>", methods = ['POST'])  # hcy
def product_info(id):
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

    d = {"productName": t['product_name'][0],
         "price": t['price'][0],
         "remain": t['remain'][0],
         "size": t['size'][0],
         "category": t['category'][0],
         "pic_url": t['pic_url'][0],
         "comments": c}
    return wrap_json_for_send(d, 'successful')


# /api/products/“商品ID"/allcomments
# input: base, {"ID"}
# output:base, {"comments":[]}
@product.route("/<id>/allcomments", methods = ['POST'])  # hcy
def allcomments(id):
    comment = """
    SELECT comment
    FROM orders
    WHERE product_id='%s'
    """ % id
    c = run_sql(comment)

    d = {"comments": c}
    return wrap_json_for_send(d, 'successful')