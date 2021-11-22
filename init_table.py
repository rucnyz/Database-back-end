import pymssql

conn = pymssql.connect(host='localhost', user="sa", password="20010511Grace")
cursor = conn.cursor()  # 创建游标
conn.autocommit(True)  # 指令立即执行，无需等待conn.commit()
create_db = """
IF OBJECT_ID('OnlineShopping', 'U') IS NULL 
CREATE DATABASE OnlineShopping
            """
cursor.execute(create_db)
conn.autocommit(False)  # 指令关闭立即执行，以后还是等待conn.commit()时再统一执行

# 创建表
# customer  -lsy
create_customer = """
IF OBJECT_ID('customer','U') IS NULL
CREATE TABLE customer(
    customer_id char(10) PRIMARY KEY,
    customer_name varchar(20) NOT NULL,
    customer_password char(10) NOT NULL,
    phone varchar(11) NOT NULL
);
"""

# supplier -lsy
create_supplier = """
IF OBJECT_ID('supplier','U') IS NULL
CREATE TABLE supplier(
    supplier_id char(10) PRIMARY KEY,
    supplier_password char(10) NOT NULL,
    supplier_name varchar(50) NOT NULL UNIQUE,
    owner varchar(20) NOT NULL,
    owner_id char(18) NOT NULL UNIQUE,
    phone varchar(11) NOT NULL
);
"""


# product -hcy
create_product = """
IF OBJECT_ID('product','U') IS NULL
CREATE TABLE product(
product_id CHAR(10) PRIMARY KEY,
product_name VARCHAR(20) NOT NULL,
price INT NOT NULL,
supplier_id CHAR(10) REFERENCES supplier(supplier_id),
remain INT NOT NULL,
size VARCHAR(10) NOT NULL,
discount REAL NOT NULL
)
"""

# order -hcy
create_order = """
IF OBJECT_ID('order','U') IS NULL
CREATE TABLE order(
order_id CHAR(10) PRIMARY KEY,
customer_id CHAR(10) REFERENCES customer(customer_id),
product_id CHAR(10) REFERENCES product(product_id),
orderdate DATE NOT NULL,
price_sum REAL NOT NULL,
quantity INT NOT NULL,
deliver_address VARCHAR(200) REFERENCES address(address_name),
receive_address VARCHAR(200) REFERENCES address(address_name),
is_return BOOLEAN NOT NULL
)
"""

# cart -nyz
create_cart = """
IF OBJECT_ID('cart','U') IS NULL 
CREATE TABLE cart(
    customer_id char(10) REFERENCES customer,
    product_id char(10) REFERENCES product,
    count int NOT NULL,
    PRIMARY KEY(customer_id, product_id),
)
"""
cursor.execute(create_cart)

# address -nyz
create_address = """
IF OBJECT_ID('address','U') IS NULL 
CREATE TABLE address(
    customer_id char(10) REFERENCES customer,
    address_name varchar(200) NOT NULL,
    nickname varchar(20) NOT NULL,
    is_customer boolean NOT NULL,
    PRIMARY KEY(customer_id, address)
)
"""
cursor.execute(create_address)

# comment -nyz
create_comment = """
IF OBJECT_ID('comment','U') IS NULL 
CREATE TABLE comment(
    comment_id char(10),
    comment varchar(200) NOT NULL,
    order_id char(10) REFERENCES order,
    PRIMARY KEY(comment_id)
)
"""
cursor.execute(create_comment)

# address

conn.commit()  # 提交数据
conn.close()
