from json import load

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import request

# 初始化app
app = Flask(__name__)

app.config.from_file("./mssql_config.json", load = load)
# 连接数据库
db = SQLAlchemy(app)

# SQLALCHEMY_DATABASE_URI

# 用于连接数据的数据库。

# SQLALCHEMY_TRACK_MODIFICATIONS

# 如果设置成 True (默认情况)，
# Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
# 这需要额外的内存， 如果不必要的可以禁用它。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


@app.route("/test", methods = ['POST', 'GET'])
def test():
    content = request.json
    print(content)
    return content


@app.route("/", methods = ['GET'])
def run():
    # cursor = db.engine.execute("select * from dbo.course")
    # ret = cursor.fetchone()
    return redirect("/test")

if __name__ == "__main__":
    app.run(debug = True, port = 5000)
