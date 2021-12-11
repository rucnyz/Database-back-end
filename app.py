from flask import Flask
from json import load

from flask_sqlalchemy import SQLAlchemy

from modules import homepage, test, customer, comment, supplier, admin, product

# 初始化app
app = Flask(__name__)

app.config.from_file("./mssql_config.json", load=load)
# 连接数据库
db = SQLAlchemy(app)

app.register_blueprint(homepage, url_prefix='/api/HomePage')
app.register_blueprint(test, url_prefix='/api/Test')
app.register_blueprint(customer, url_prefix='/api/customer')
app.register_blueprint(comment, url_prefix='/api/comment')
app.register_blueprint(supplier, url_preflix='/api/supplier')
app.register_blueprint(admin, url_preflix='/api/admin')
app.register_blueprint(product, url_preflix='/api/product')

@app.route("/")
def home():
    return "welcome to home"


if __name__ == "__main__":
    app.run(debug=True, port=5200, host="0.0.0.0")
