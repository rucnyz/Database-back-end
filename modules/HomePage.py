from flask import Blueprint,request,current_app
from flask_sqlalchemy import SQLAlchemy
from utils import run_sql
from json import dumps
homepage = Blueprint('homepage', __name__)

db = SQLAlchemy()

@homepage.route('/')
def show():
    return 'This is HomePage test.'

# 	a. 此处商品展示仅有缩略图与商品名。
# /api/HomePage/getProduct
# input:base, {"needNumber":xx（数字）}
# output: base, {{"商品id"：id，"商品图片"：图片url，"商品名称"：名称，"商品价格"：价格},{……},{……}}
@homepage.route("/getProduct", methods=['POST', 'GET'])  # zzm
def get_homePage():
    number = request.args['needNumber']
    get_homePage = """
    SELECT TOP %s product_id, pic_url, product_name, price 
    FROM product p 
    ORDER BY NewID()
    """ % number

    tuple = run_sql(get_homePage,db)
    column = ["商品ID", "商品图片", "商品名称", "商品价格"]
    d = [dict(zip(column,tuple[i])) for i in range(len(tuple))]

    return dumps(d)

#  /api/HomePage/getCategory（固定栏）
# input: base
# output: base ,{"number":xx（数字）,"分类”:[……, ……,……]}
@homepage.route("/getCategory", methods=['POST', 'GET'])  # zzm
def get_homepage_category():
    get_homepage_category = """
    select distinct p.category 
    from product p       
    
    """

    tuple = run_sql(get_homepage_category,db)[0]
    d = {"number": len(tuple), "分类": tuple}

    return dumps(d)