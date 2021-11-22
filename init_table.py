import pymssql

conn = pymssql.connect(host='localhost', user="sa", password="20010511Grace")
cursor = conn.cursor()  # 创建游标
conn.autocommit(True)  # 指令立即执行，无需等待conn.commit()
create_db = """
IF OBJECT_ID('test5', 'U') IS NULL 
CREATE DATABASE test5
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
# supplier_name：店铺名; owner：店铺负责人名字 ;
cursor.execute(create_supplier)


# address -nyz
create_address_supplier = """
IF OBJECT_ID('address_supplier', 'U') IS NULL
CREATE TABLE address_supplier(
    supplier_id char(10) REFERENCES supplier(supplier_id),
    address_name varchar(200) NOT NULL,
    nickname varchar(20) NOT NULL,
    PRIMARY KEY(supplier_id, address_name)
);
"""
cursor.execute(create_address_supplier)

create_address_customer = """
IF OBJECT_ID('address_customer', 'U') IS NULL
CREATE TABLE address_customer(
    customer_id char(10) REFERENCES customer(customer_id),
    address_name varchar(200) NOT NULL,
    nickname varchar(20) NOT NULL,
    PRIMARY KEY(customer_id, address_name)
);
"""
cursor.execute(create_address_customer)


# product -hcy
create_product = """
IF OBJECT_ID('product', 'U') IS NULL
CREATE TABLE product(
    product_id CHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price INT NOT NULL,
    supplier_id CHAR(10) REFERENCES supplier(supplier_id),
    remain INT NOT NULL,
    size VARCHAR(10) NOT NULL,
    discount REAL NOT NULL
);
"""

# order -hcy
create_orders = """
IF OBJECT_ID('orders', 'U') IS NULL
CREATE TABLE orders(
    order_id CHAR(10) PRIMARY KEY,
    customer_id CHAR(10),
    supplier_id CHAR(10),
    product_id CHAR(10) REFERENCES product(product_id),
    orderdate DATE NOT NULL,
    price_sum REAL NOT NULL,
    quantity INT NOT NULL,
    deliver_address VARCHAR(200),
    receive_address VARCHAR(200),
    FOREIGN KEY(customer_id, deliver_address) REFERENCES address_customer(customer_id, address_name),
    FOREIGN KEY(supplier_id, receive_address) REFERENCES address_supplier(supplier_id, address_name),
    is_return BIT NOT NULL
);
"""
# price_sum = price * quantity * discount
# deliver_address对应的is_customer为false，receive_address对应的is_customer为true
cursor.execute(create_orders)


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
cursor.execute(create_cart)


# comment -nyz
create_comment = """
IF OBJECT_ID('comment', 'U') IS NULL
CREATE TABLE comment(
    comment_id char(10),
    comment varchar(200) NOT NULL,
    order_id char(10) REFERENCES order,
    PRIMARY KEY(comment_id)
);
"""
cursor.execute(create_comment)

# address

conn.commit()  # 提交数据
conn.close()
