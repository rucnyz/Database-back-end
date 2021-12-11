from flask import Blueprint,request,current_app
from flask_sqlalchemy import SQLAlchemy
from utils import run_sql
test = Blueprint('test', __name__)

db = SQLAlchemy()

@test.route("/")
def test_main():
    return "this is page for test"

@test.route("/test_json", methods=['POST'])
def test_json():
    content = request.json
    print(content)
    return content

@test.route("test_db", methods=['POST'])
def test_db():
    number = request.json['needNumber']
    getHomePage = """
        SELECT TOP %s product_id, pic_url, product_name, price 
        FROM product p 
        ORDER BY NewID()
        """ % number
    t = run_sql(getHomePage)
    column = ["商品ID", "商品图片", "商品名称", "商品价格"]
    d = {"detail": [dict(zip(column, t[i])) for i in range(len(t))]}
    print(d)
    return "hello"
    