# -*- coding: utf-8 -*-
import sys
import random
from utils import run_sql
from faker import Faker
import hashlib
import pandas as pd
# 注意
# 顾客id：C000000051
# 原始密码：_OmUuV+ZE5
# hash+截取之后的存储在数据库中：17a21b26d7
# phone：15204814455
# 作为前端测试使用


sys.path.append(".")
Faker.seed(135)
fake = Faker(locale = 'zh_CN')

n = 50  # 生成的数据数量


def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    res = sha256.hexdigest()[:10]
    return res


def get_col(sql_list, n):
    sql_col = [x[n] for x in sql_list]
    return sql_col


def insert_customer():
    get_number = """
    SELECT ISNULL(COUNT(*),0)
    FROM customer
    """
    number = get_col(run_sql(get_number), 0)  # 数值型
    for i in range(n):
        password_temp = fake.password(length = 10, upper_case = True, lower_case = True)

        insert_customer = """
        insert into customer(customer_id, customer_phonenumber, customer_password)
        values('%s','%s','%s');
        """ % ('C' + str(number[0] + i + 1).zfill(9),  # 编号
               fake.phone_number(),
               hash_password(password_temp))
        run_sql(insert_customer)


def insert_supplier():
    get_number = """
    SELECT ISNULL(COUNT(*),0)
    FROM supplier
    """

    number = get_col(run_sql(get_number), 0)
    for i in range(n):
        password_temp = fake.password(length = 10, upper_case = True, lower_case = True)
        insert_supplier = """
        insert into supplier(supplier_id, supplier_password, supplier_name, owner_name, owner_id)
        values('%s','%s','%s','%s','%s')
        """ % ('S' + str(number[0] + i + 1).zfill(9),
               hash_password(password_temp),
               fake.company() + str(i),  # supplier_name是店铺名称
               fake.name(),
               fake.ssn(min_age = 18, max_age = 90))  # owner_id 是店铺主的身份证号
        run_sql(insert_supplier)


def insert_info_supplier():
    get_id = """
    SELECT supplier_id
    FROM supplier
    """
    supplier_id = get_col(run_sql(get_id), 0)  # 给所有的supplier都插入info
    # supplier_id = random.sample(cursor.fetchall() , n) #从已有的id中随机取出n个
    for i in range(len(supplier_id)):
        insert_info_supplier = """
        INSERT INTO info_supplier(supplier_id, address_name, nickname, phone)
        values('%s','%s','%s','%s')
        """ % (supplier_id[i],
               fake.address(),
               fake.first_name(),  # 生成收货昵称
               fake.phone_number())
        run_sql(insert_info_supplier)


def insert_info_customer():
    get_id = """
    SELECT customer_id
    FROM customer
    """
    customer_id = get_col(run_sql(get_id), 0)
    # customer_id = random.sample(cursor.fetchall(), n)
    for i in range(len(customer_id)):
        insert_info_customer = """
        insert into info_customer(customer_id, address_name, nickname, phone)
        values('%s','%s','%s','%s')
        """ % (customer_id[i],
               fake.address(),
               fake.first_name(),  # 随机生成收货昵称
               fake.phone_number())
        run_sql(insert_info_customer)


def insert_product():
    product_info = pd.read_csv("product_info.csv", encoding = "GBK")
    product_name = product_info[u"商品名称"]
    pic_url = product_info["封面图链接"]
    price = product_info["价格"]
    get_number = """
    SELECT ISNULL(COUNT(*), 0)
    FROM product
    """
    number = get_col(run_sql(get_number), 0)

    get_id = """
    SELECT supplier_id
    FROM supplier
    """

    supplier_id = get_col(run_sql(get_id), 0)
    for i in range(len(supplier_id)):
        insert_product = """
        INSERT INTO product(product_id, product_name, price, supplier_id, remain, size, discount, category, pic_url)
        values('%s','%s','%u','%s','%u','%s','%f','%s','%s')
        """ % ('P' + str(number[0] + i + 1).zfill(9),  # 编号
               product_name[i],
               price[i],
               supplier_id[i],
               random.randint(0, 9999),
               fake.word(ext_word_list = ['S', 'M', 'L', 'XL']),  # 尺寸SML XL
               round(random.random(), 2),
               fake.word(ext_word_list = ['家用电器', '数码设备', '家居', '服装', '配饰', '美妆', '鞋类', '食品', '文娱', '其他']),
               pic_url[i])
        run_sql(insert_product)


def insert_orders():
    get_number = """
    SELECT ISNULL(COUNT(*), 0)
    FROM product
    """
    number = get_col(run_sql(get_number), 0)

    get_need_s = """
    SELECT s.supplier_id, p.product_id, p.price*(1-p.discount)
    FROM product p, supplier s
    WHERE s.supplier_id = p.supplier_id
    """
    need = run_sql(get_need_s)  # list类型
    supplier_id = random.sample(get_col(need, 0), n)  # 随机挑选n个
    product_id = random.sample(get_col(need, 1), n)
    price_unit = random.sample(get_col(need, 2), n)

    get_customer_id = """
    SELECT customer_id
    FROM customer
    """
    customer_id = random.sample(get_col(run_sql(get_customer_id), 0), n)

    quantity = [random.randint(0, 9999) for x in range(n)]

    for i in range(n):
        # 先查人对应的地址    
        get_address_c = """
        SELECT  address_name
        FROM  info_customer
        WHERE customer_id = '%s'
        """ % customer_id[i]
        address_c = random.choice(get_col(run_sql(get_address_c), 0))  # 只要一个地址就行

        get_address_s = """
        SELECT  address_name
        FROM  info_supplier
        WHERE supplier_id = '%s'
        """ % supplier_id[i]
        address_s = random.choice(get_col(run_sql(get_address_s), 0))

        insert_orders = """
        INSERT INTO orders(order_id, customer_id, supplier_id, product_id, orderdate, quantity, price_sum, deliver_address, receive_address, is_return, comment)
        VALUES('%s','%s','%s','%s','%s','%u','%f','%s','%s','%u','%s')
        """ % ('O' + str(number[0] + i + 1).zfill(9),
               customer_id[i],
               supplier_id[i],
               product_id[i],
               fake.date_this_decade(before_today = True, after_today = False),  # 本年代中的日期
               quantity[i],
               quantity[i] * price_unit[i],
               address_s,
               address_c,
               random.randint(0, 1),
               fake.paragraph(nb_sentences = 2)[:100]  # varchar(200)
               )
        run_sql(insert_orders)


def insert_cart():
    get_customer_id = """
        SELECT  customer_id
        FROM  customer
        """
    customer_id = get_col(run_sql(get_customer_id), 0)

    get_product_id = """
    SELECT  product_id
    FROM  product
    """
    product_id = random.sample(get_col(run_sql(get_product_id), 0), len(customer_id))

    for i in range(0, len(customer_id)):
        insert_cart = """
        INSERT INTO cart(customer_id , product_id, count)
        VALUES('%s', '%s', '%u')
        """ % (customer_id[i],
               product_id[i],
               random.randint(0, 9999)
               )
        run_sql(insert_cart)


def insert_fake():
    use_db = """
    USE OnlineShopping
                """
    delet = """

    """
    run_sql(delet)

    run_sql(use_db)
    insert_customer()
    insert_supplier()
    insert_info_customer()
    insert_info_supplier()
    insert_product()
    insert_orders()
    insert_cart()


insert_fake()  # 执行所有插入
# cursor.close()
# conn.close()
