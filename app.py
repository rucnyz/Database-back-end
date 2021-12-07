from json import load

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from modules import db_test, db_homepage, db_customer, db_comment, db_supplier
from modules import homepage, test, customer, comment, supplier

# 初始化app
app = Flask(__name__)

app.config.from_file("./mssql_config.json", load = load)
# 连接数据库
db = SQLAlchemy(app)

app.register_blueprint(homepage, url_prefix = '/api/HomePage')
app.register_blueprint(test, url_prefix = '/api/Test')
app.register_blueprint(customer, url_prefix = '/api/customer')
app.register_blueprint(comment, url_prefix = '/api/comment')
app.register_blueprint(supplier, url_preflix = '/api/supplier')

db_test.init_app(app)
db_homepage.init_app(app)
db_customer.init_app(app)
db_comment.init_app(app)
db_supplier.init_app(app)


@app.route("/")
def home():
    return "welcome to home"


if __name__ == "__main__":
    app.run(debug = True, port = 5200, host = "0.0.0.0")
