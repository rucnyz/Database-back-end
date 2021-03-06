import sys

sys.path.append("..")
import platform

from utils import run_sql

if platform.system() == 'Windows':
    create_db = """
    commit;
    IF DB_ID('OnlineShopping') IS NULL 
    CREATE DATABASE OnlineShopping
                """
else:
    create_db = """
        commit;
        IF DB_ID('OnlineShopping') IS NULL 
        CREATE DATABASE OnlineShopping COLLATE Chinese_Simplified_Stroke_Order_100_CI_AS_SC_UTF8
                    """
# DB_ID对应数据库 OBJECT_ID对应表

run_sql(create_db)
# conn.autocommit(False)  # 指令关闭立即执行，以后还是等待conn.commit()时再统一执行

# use数据库
use = """
USE OnlineShopping"""
run_sql(use)

use_db = """
USE OnlineShopping
            """
run_sql(use_db)
# 创建表
# customer  -lsy
create_customer = """
IF OBJECT_ID('customer', 'U') IS NULL
CREATE TABLE customer(
    customer_id char(10) PRIMARY KEY,
    customer_phonenumber varchar(20) UNIQUE,
    customer_password char(10) NOT NULL,
    customer_nickname varchar(20),
    customer_realname varchar(20) NOT NULL
);
"""
run_sql(create_customer)

# supplier -lsy
create_supplier = """
IF OBJECT_ID('supplier', 'U') IS NULL
CREATE TABLE supplier(
    supplier_id char(10) PRIMARY KEY,
    supplier_password char(10) NOT NULL,
    supplier_name varchar(50) NOT NULL UNIQUE,
    owner_name varchar(20) NOT NULL,
    owner_id char(18) NOT NULL  -- UNIQUE
);
"""
# supplier_name：店铺名; owner：店铺负责人名字 ;
run_sql(create_supplier)

# address -nyz
create_info_supplier = """
IF OBJECT_ID('info_supplier', 'U') IS NULL
CREATE TABLE info_supplier(
    supplier_id char(10) REFERENCES supplier(supplier_id),
    address_name varchar(200) NOT NULL,
    nickname varchar(20) NOT NULL,
    PRIMARY KEY(supplier_id),
    phone varchar(11) NOT NULL
);
"""
run_sql(create_info_supplier)

create_info_customer = """
IF OBJECT_ID('info_customer', 'U') IS NULL
CREATE TABLE info_customer(
    customer_id char(10) REFERENCES customer(customer_id),
    address_name varchar(200) NOT NULL, -- 不用把地址拆成省市区，查询的时候直接模糊查"省"即可
    nickname varchar(20) NOT NULL,
    phone varchar(11) NOT NULL,
    PRIMARY KEY(customer_id)
);
"""
run_sql(create_info_customer)

# product -hcy
create_product = """
IF OBJECT_ID('product', 'U') IS NULL
CREATE TABLE product(
    product_id CHAR(10) PRIMARY KEY,
    product_name VARCHAR(500) NOT NULL,
    price INT NOT NULL,
    supplier_id CHAR(10) REFERENCES supplier(supplier_id),
    remain INT NOT NULL,
    size VARCHAR(10) NOT NULL,
    discount REAL NOT NULL,
    category VARCHAR(50) NOT NULL,
    pic_url VARCHAR(500) NOT NULL
);
"""
run_sql(create_product)

# order -hcy 订单表
create_orders = """
IF OBJECT_ID('orders', 'U') IS NULL
CREATE TABLE orders(
    order_id CHAR(10) PRIMARY KEY,
    customer_id CHAR(10) REFERENCES customer(customer_id),
    supplier_id CHAR(10) REFERENCES supplier(supplier_id),
    product_id CHAR(10) REFERENCES product(product_id),
    orderdate DATETIME NOT NULL,
    price_sum REAL NOT NULL,
    quantity INT NOT NULL,
    deliver_address VARCHAR(200) NOT NULL,
    receive_address VARCHAR(200) NOT NULL,
    is_return BIT NOT NULL,
    comment VARCHAR(200)
);
"""

# ## 此处我们没有汇总订单表，orders表相当于订单明细表，可以建立汇总订单视图
# create_view_sum_orders = """
# IF OBJECT_ID('sum_orders', 'U') IS NULL
# CREATE VIEW sum_orders
# AS
#     SELECT orderdate, supplier_id, customer_id, sum(price_sum) sum_price, count(*) count, deliver_address, receive_address
#     FROM orders
#     GROUP BY orderdate, supplier_id, customer_id, deliver_address, receive_address
#     ORDER BY orderdate, supplier_id, customer_id
# );
# """


# price_sum = price * quantity * discount
# deliver_address对应的is_customer为false，receive_address对应的is_customer为true
run_sql(create_orders)

# cart -nyz
create_cart = """
IF OBJECT_ID('cart', 'U') IS NULL
CREATE TABLE cart(
    customer_id char(10) REFERENCES customer(customer_id),
    product_id char(10) REFERENCES product(product_id),
    count int NOT NULL,
    PRIMARY KEY(customer_id, product_id)
);
"""
run_sql(create_cart)

# admin -zzm
create_admin = """
IF OBJECT_ID('admin', 'U') IS NULL
CREATE TABLE admin(
    admin_id char(10) NOT NULL,
    admin_name char(10) NOT NULL,
    admin_password char(10) NOT NULL,
    PRIMARY KEY(admin_id)
)
"""
run_sql(create_admin)
init_admin = """
INSERT 
INTO admin
VALUES('A000000001', 'administer', 'administer')
"""
run_sql(init_admin)

# # comment -nyz 删掉了 合到订单表里
# create_comment = """
# IF OBJECT_ID('comment', 'U') IS NULL
# CREATE TABLE comment(
#     comment_id char(10),
#     comment varchar(200) NOT NULL,
#     order_id char(10) REFERENCES orders(order_id),
#     PRIMARY KEY(comment_id)
# );
# """
# run_sql(create_comment)

# address
