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

@test.route("test_db")
def test_db():
    res = run_sql("select * from customer",db)
    print(res)
    return "hello"
    