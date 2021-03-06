import os
import pyodbc
import threading
from sqlalchemy.engine import URL
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine, text


class Database:
    _instance_lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        # 线程安全的单例模式
        if not hasattr(cls, 'instance_dict'):
            Database.instance_dict = {}

        if str(cls) not in Database.instance_dict.keys():
            with Database._instance_lock:
                _instance = super().__new__(cls)
                Database.instance_dict[str(cls)] = _instance

        return Database.instance_dict[str(cls)]

    def __init__(self, dsn_name: str):
        if os.getcwd().endswith("script"):
            curpath = os.getcwd() + '/../dsn/'
        else:
            curpath = os.getcwd() + '/dsn/'
        pyodbc.pooling = False
        self.dsn = curpath + dsn_name
        engine_prarm = URL.create(
            "mssql+pyodbc", query = {"odbc_connect": f"FILEDSN={self.dsn}"})
        self.connect_pool = QueuePool(
            self.__get_connection, pool_size = 200, max_overflow = 40, pre_ping = True)
        self.engine = create_engine(engine_prarm, pool = self.connect_pool)

    def __get_connection(self):
        odbc_param = (f"FILEDSN={self.dsn}")
        cnxn = pyodbc.connect(odbc_param)
        return cnxn

    def status(self):
        return self.connect_pool.status()

    def test(self):
        import time
        with self.engine.connect() as conn:
            res = conn.execute(text("SELECT @@SPID")).all()
            time.sleep(0.5)
        return res

    def query(self, query_sql: str, query_para: dict = None):
        with self.engine.begin() as conn:
            query_text = text(query_sql)
            query = conn.execute(query_text, query_para)
            try:
                key = list(query.keys())
                value = [tuple(x) for x in query.all()]
                res = [dict(zip(key,x)) for x in value]
            except BaseException as e:
                res = None
        return res

    def trans(self, sqlDict: dict[str, dict]):
        with self.engine.begin() as conn:
            for T_sql, param in sqlDict.items():
               conn.execute(text(T_sql), param)


class Database_sa(Database):
    def __init__(self):
        super().__init__("sa.dsn")


class Database_customer(Database):
    def __init__(self):
        super().__init__("customer.dsn")


class Database_supplier(Database):
    def __init__(self):
        super().__init__("supplier.dsn")


class Database_admin(Database):
    def __init__(self):
        super().__init__("admin.dsn")


user_dict = {
    "sa": Database_sa(),
    "customer": Database_customer(),
    "supplier": Database_supplier(),
    "admin": Database_admin()
}


def run_sql(T_sql: str, param: dict = None, user = "sa"):
    return user_dict[user].query(T_sql, param)


def run_sqls(sqlDict: dict[str, dict], user="sa"):
    # 注意：此方法如果其中一个查询失败，其他查询不受影响
    # 若返回的key中没有某一语句，则该语句执行失败
    # 开启了autocommit, 本方法效率和run_sql写循环其实是一样的
    result = {}
    error = {}
    for T_sql, param in sqlDict.items():
        try:
            result[T_sql] = run_sql(T_sql, param, user)
        except BaseException as e:
            error[T_sql] = str(e)
    return result, error


def run_trans(sqlDict: dict[str, dict], user="sa"):
    user_dict[user].trans(sqlDict)


def get_url(user = "sa"):
    return user_dict[user].engine.url



if __name__ == "__main__":
    sel_customer = """
        SELECT * FROM customer
    """
    sel_supplier="""
        SELECT * FROM supplier
    """
    sel_value = """
        SELECT * FROM customer WHERE customer_id=:cus_id
    """

    insert_test = """INSERT
    INTO customer(customer_id, customer_phonenumber, customer_password)
    VALUES('C000001000', '123456789123', '4e116d4fa2')"""
    # print(run_sql(sel_customer))
    # print(run_sql(sel_value,{"cus_id":"C000000044"}))
    try:
        run_trans({insert_test:None,sel_supplier:None})
    except:
        print("error")
    print(run_sql(sel_value,{"cus_id":'C000001000'}))
    print(run_sql("DELETE FROM customer WHERE customer_id=:cus_id",{"cus_id":"C000001000"}))
    print(run_sql(sel_value,{"cus_id":'C000001000'}))
    # import time
    # import random

    # class Test(threading.Thread):
    #     def __init__(self, threadID, name, counter):
    #         threading.Thread.__init__(self)
    #         self.threadID = threadID
    #         self.name = name
    #         self.counter = counter

    #     def run(self):
    #         test = Database_sa()
    #         time.sleep(0.3 * random.random())
    #         test.test()
    #         print(test.status())

    # for i in range(1000):
    #     test = Test(i, "thread-"+str(i), i)
    #     test.start()
    # for i in range(10):
    #     admin = Database_admin()
    #     print(admin)
    #     base = Database_sa()
    #     print(base)
    #     print("----------------------")
