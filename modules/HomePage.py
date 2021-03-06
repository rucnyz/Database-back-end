from flask import Blueprint, request
from flask_sqlalchemy import SQLAlchemy

from utils import run_sql, wrap_json_for_send

homepage = Blueprint('homepage', __name__)

db = SQLAlchemy()


@homepage.route('/')
def show():
    return 'This is HomePage test.'


# 	a. 此处商品展示仅有缩略图与商品名。【已测试】
# /api/HomePage/getProduct
# input:base, {"needNumber":xx（数字）, "page":xx}
# output: base, {{"商品id"：id，"商品图片"：图片url，"商品名称"：名称，"商品价格"：价格},{……},{……}}
@homepage.route("/getProduct", methods = ['POST', 'GET'])  # zzm
def get_homePage():
    number = request.args['needNumber']
    page = request.args['page']
    out_num = (int(page) - 1) * int(number)
    getSize = """
    SELECT count(*) 
    FROM product
    """
    getHomePage = """
    SELECT TOP %s p1.product_id, p1.pic_url, p1.product_name, p1.price 
    FROM product p1
    WHERE p1.product_id NOT IN ( SELECT TOP %s p2.product_id
                                  FROM product p2)
    ORDER BY NewID()
    """ % (number, out_num)

    t = run_sql(getHomePage)
    size = run_sql(getSize)
    column = ["ID", "product_pic", "product_name", "price"]
    d = {"totalSize": size[0][''], "detail": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    return wrap_json_for_send(d, "successful")


#  /api/HomePage/getCategory（固定栏）zzm【已测试】
# input: base
# output: base ,{"number":xx（数字）,"分类”:[……, ……,……]}
@homepage.route("/getCategory", methods = ['POST', 'GET'])  # zzm
def get_homepage_category():
    getHomepageCategory = """
    select distinct p.category cat
    from product p       
    """
    t = run_sql(getHomepageCategory)
    t = [i['cat'] for i in t]
    d = {"number": len(t), "category": t}

    return wrap_json_for_send(d, "successful")


#  /api/HomePage/getProductInCat   用于返回特定种类商品。zzm【已测试】
# input: base,{"category":xx}
# output: base ,{{"商品id"：id，"商品图片"：图片url，"商品名称"：名称，"商品价格"：价格},{……},{……}}
@homepage.route("/getProductInCat", methods = ['POST', 'GET'])  # zzm
def return_product_in_category():
    cat = request.json['category']

    returnProductInCategory = """
    select product_id, pic_url, product_name, price
    from product p       
    where p.category=:cat
    """

    t = run_sql(returnProductInCategory, {"cat": cat})
    column = ["ID", "product_pic", "product_name", "price"]
    d = {"detail": [dict(zip(column, t[i].values())) for i in range(len(t))]}

    return wrap_json_for_send(d, "successful")


# 5. 搜索含某关键词（可限制类别）的商品[已测试]
# /api/HomePage/getProductInCond 用于返回特定关键词商品。
# input: base,{"keywords", ”category“, "needNumber", "page"}
# output: base, {{"product_id":id, "pic_url":图片url, "product_name":名称, "price"：价格},{……},{……}}
@homepage.route("/getProductInCond", methods = ['POST', 'GET'])  # lsy
def get_product_in_cond():
    cat = request.args['category']
    keywords = request.args['keywords']
    number = request.args['needNumber']
    page = request.args['page']
    out_num = (int(page) - 1) * int(number)
    product_name_vague = '%' + keywords + '%'
    if len(cat) == 0:
        get_product = """
            SELECT TOP %s p1.product_id, p1.pic_url, p1.product_name, p1.price 
            FROM product p1
            WHERE p1.product_name LIKE :keywords AND p1.product_id NOT IN ( SELECT TOP %s p2.product_id
                                          FROM product p2 WHERE p2.product_name LIKE :keywords)
            """ % (number, out_num)
        get_size = """
                SELECT count(*)
                    FROM product p  
                    WHERE product_name LIKE :keywords     
                    """
        t = run_sql(get_product, {"keywords": product_name_vague})
        size = run_sql(get_size, {"keywords": product_name_vague})
    else:
        get_product = """
                    SELECT TOP %s p1.product_id, p1.pic_url, p1.product_name, p1.price
                    FROM product p1  
                    WHERE product_name LIKE :keywords AND category = :category 
                    AND p1.product_id NOT IN ( SELECT TOP %s p2.product_id
                                          FROM product p2 WHERE p2.product_name LIKE :keywords AND category = :category)
                    """ % (number, out_num)
        get_size = """
                        SELECT count(*)
                        FROM product p  
                        WHERE product_name LIKE :keywords AND category = :category
                   """
        t = run_sql(get_product, {"keywords": product_name_vague, "category": cat})
        size = run_sql(get_size, {"keywords": product_name_vague, "category": cat})

    column = ["ID", "product_pic", "product_name", "price"]
    d = {"totalSize": size[0][''], "detail": [dict(zip(column, t[i].values())) for i in range(len(t))]}
    return wrap_json_for_send(d, "successful")


#  /api/HomePage/search_product   用于返回特定关键词商品。
# input: base,{"keywords", ”category“}
# output: base, {{"商品id":id, "商品图片":图片url, "商品名称":名称, "商品价格"：价格},{……},{……}}
@homepage.route("/search_product ", methods = ['POST', 'GET'])  # zzm
def search_product():
    cat = request.json['category']
    keywords = request.json['keywords']
    get_cat_product = """
    SELECT product_id, pic_url, product_name, price
    FROM product p
    WHERE p.category='%s' AND p.product_name LIKE '%s'
    """ % (cat, keywords)
    get_product = """
    SELECT product_id, pic_url, product_name, price
    FROM product p
    WHERE p.product_name LIKE '%s'
    """ % keywords
    if cat.isspace():
        t = run_sql(get_product)
    else:
        t = run_sql(get_cat_product)
    column = ["商品ID", "商品图片", "商品名称", "商品价格"]
    d = {"detail": [dict(zip(column, t[i])) for i in range(len(t))]}
    return wrap_json_for_send(d, "successful")
