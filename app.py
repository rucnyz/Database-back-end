from flask import Flask
from json import load
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

# 初始化app
app = Flask(__name__)

app.config.from_file("./mssql_config.json",load=load)
# 连接数据库
db = SQLAlchemy(app)

# SQLALCHEMY_DATABASE_URI

# 用于连接数据的数据库。

# SQLALCHEMY_TRACK_MODIFICATIONS

# 如果设置成 True (默认情况)，
# Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
# 这需要额外的内存， 如果不必要的可以禁用它。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# 得到SQLAlchemy对象


@app.route("/")
def run():
    # 是这一句出问题了，似乎不能在执行的函数内初始化数据库的连接，
    # 而需要放在外部，注释掉就正常了
    # db = SQLAlchemy(app, use_native_unicode = 'utf8')
    cursor = db.engine.execute("select * from master.dbo.sysdatabases")
    ret = cursor.fetchone()
    return str(ret)


app.run(debug = True)
