from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
# 还需要安装pymysql库
# 初始化app
app = Flask(__name__)
db = SQLAlchemy(app)
# 连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:nyz010622@localhost/test'

@app.route("/")
def hello():
    # test = db.engine.execute("select * from test")
    return "hello,world"


# SQLALCHEMY_DATABASE_URI

# 用于连接数据的数据库。

# SQLALCHEMY_TRACK_MODIFICATIONS

# 如果设置成 True (默认情况)，

# Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。

# 这需要额外的内存， 如果不必要的可以禁用它。

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# 得到SQLAlchemy对象

db = SQLAlchemy(app, use_native_unicode='utf8')

# 然后创建model对象

class User(db.Model):

    __tablename__ = 'user_list' #(设置表名)

    id = db.Column(db.Integer, primary_key=True) #(设置主键)

    username = db.Column(db.String(255), unique=True)

    password = db.Column(db.String(255), unique=True)

# 返回一个可以用来表示对象的可打印字符串：(相当于java的toString)

    def __repr__(self):

        return '' % (self.username, self.password)

    # 操作数据库

    # 增

    def add_object(user):

        db.session.add(user)

        db.session.commit()

        print("添加 % r 完成" % user.__repr__)

        user = User()

        user.username = '占三'

        user.password = '123456'


    # 查 (用到and的时候需要导入库from sqlalchemy import and_)

    def query_object(user, query_condition_u, query_condition_p):

        result = user.query.filter(and_(user.username == query_condition_u, user.password == query_condition_p))

        print("查询 % r 完成" % user.__repr__)

        return result

    # 删

    def delete_object(user):

        result = user.query.filter(user.username == '11111').all()

        db.session.delete(result)

        db.session.commit()

    #改

    def update_object(user):

        result = user.query.filter(user.username == '111111').all()

        result.title = 'success2018'

        db.session.commit()