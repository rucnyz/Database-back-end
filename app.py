from flask import Flask
from json import load
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

# 初始化app
app = Flask(__name__)

app.config.from_file("./mssql_config.json", load = load)
# 连接数据库
db = SQLAlchemy(app)

@app.route("/")
def run():
    cursor = db.engine.execute("select * from master.dbo.sysdatabases")
    ret = cursor.fetchone()
    return str(ret)


app.run(debug = True)
