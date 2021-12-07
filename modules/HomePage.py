from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

homepage = Blueprint('homepage', __name__)

db = SQLAlchemy()


@homepage.route('/')
def show():
    return 'This is HomePage test.'


# 	a. 此处商品展示仅有缩略图与商品名。
# /api/HomePage/getProduct
# input:base, {"needNumber":xx（数字）}
# output: base, {{"商品id"：id，"商品图片"：图片url，"商品名称"：名称，"商品价格"：价格},{……},{……}}
@homepage.route("/getProduct", methods = ['POST', 'GET'])  # zzm
def get_homePage():
    number = request.args['needNumber']
    getHomePage = """
    SELECT TOP %s product_id, pic_url, product_name, price 
    FROM product p 
    ORDER BY NewID()
    """ % number

    t = run_sql(getHomePage, db)
    column = ["商品ID", "商品图片", "商品名称", "商品价格"]
    d = {"detail": [dict(zip(column, t[i])) for i in range(len(t))]}

    return wrap_json_for_send(d, "successful")


#  /api/HomePage/getCategory（固定栏）
# input: base
# output: base ,{"number":xx（数字）,"分类”:[……, ……,……]}
@homepage.route("/getCategory", methods = ['POST', 'GET'])  # zzm
def get_homepage_category():
    getHomepageCategory = """
    select distinct p.category 
    from product p       
    
    """

    t = run_sql(getHomepageCategory, db)[0]
    d = {"number": len(t), "分类": t}

    return wrap_json_for_send(d, "successful")
