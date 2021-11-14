from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
# 还需要安装pymysql库
# 初始化app
app = Flask(__name__)
db = SQLAlchemy(app)
# 连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:nyz010622@localhost/test'




# SQLALCHEMY_DATABASE_URI

# 用于连接数据的数据库。

# SQLALCHEMY_TRACK_MODIFICATIONS

# 如果设置成 True (默认情况)，
# Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
# 这需要额外的内存， 如果不必要的可以禁用它。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 得到SQLAlchemy对象

db = SQLAlchemy(app, use_native_unicode='utf8')

@app.route("/")
def hello():
    cursor = db.engine.execute("select * from dept")
    ret = cursor.fetchone()
    return str(ret)

