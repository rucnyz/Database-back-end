# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
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
Faker.seed(135)

Faker.seed(135)
fake = Faker(locale = 'zh_CN')

n = 50  # 生成的数据数量


def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    res = sha256.hexdigest()[:10]
    return res


def get_col(sql_list, col_name):
    sql_col = [x[col_name] for x in sql_list]
    return sql_col


def insert_customer():
    get_number = """
    SELECT ISNULL(COUNT(*),0) as number
    FROM customer
    """
    number = get_col(run_sql(get_number), "number")  # 数值型
    df_insert_customer = pd.DataFrame(columns = ["customer_id", "phone_number", "password", "password_hashed"])
    for i in range(n):
        customer_id = 'C' + str(number[0] + i + 1).zfill(9)
        phone_number = fake.phone_number()
        password = fake.password(length = 10, upper_case = True, lower_case = True)
        password_hashed = hash_password(password)
        df_insert_customer.loc[i] = [customer_id, phone_number, password, password_hashed]

        insert_customer = """
        insert into customer(customer_id, customer_phonenumber, customer_password)
        values(:customer_id,:phone_number,:password);
        """
        run_sql(insert_customer,
                {"customer_id": customer_id, "phone_number": phone_number, "password": password_hashed})
    df_insert_customer.to_csv("../fake_data/insert_customer.csv")


def insert_supplier():
    get_number = """
    SELECT ISNULL(COUNT(*),0) as number
    FROM supplier
    """

    number = get_col(run_sql(get_number), "number")
    df_insert_supplier = pd.DataFrame(
        columns = ["supplier_id", "supplier_password", "supplier_password_hashed", "supplier_name", "owner_name",
                   "owner_id"])
    for i in range(n):
        supplier_id = 'S' + str(number[0] + i + 1).zfill(9)
        supplier_password = fake.password(length = 10, upper_case = True, lower_case = True)
        supplier_password_hashed = hash_password(supplier_password)
        supplier_name = fake.company() + str(i)  # supplier_name是店铺名称
        owner_name = fake.name()
        owner_id = fake.ssn(min_age = 18, max_age = 90)  # owner_id 是店铺主的身份证号
        df_insert_supplier.loc[i] = [supplier_id, supplier_password, supplier_password_hashed, supplier_name,
                                     owner_name, owner_id]
        insert_supplier = """
        insert into supplier(supplier_id, supplier_password, supplier_name, owner_name, owner_id)
        values(:supplier_id,:supplier_password,:supplier_name,:owner_name,:owner_id)
        """
        # % ('S' + str(number[0] + i + 1).zfill(9),
        #        hash_password(supplier_password),
        #        fake.company() + str(i),  # supplier_name是店铺名称
        #        fake.name(),
        #        fake.ssn(min_age = 18, max_age = 90))  # owner_id 是店铺主的身份证号
        run_sql(insert_supplier, {"supplier_id": supplier_id,
                                  "supplier_password": supplier_password_hashed,
                                  "supplier_name": supplier_name,
                                  "owner_name": owner_name,
                                  "owner_id": owner_id
                                  })
    df_insert_supplier.to_csv("../fake_data/insert_supplier.csv")


def insert_info_supplier():
    get_id = """
    SELECT supplier_id
    FROM supplier
    """
    supplier_id = get_col(run_sql(get_id), "supplier_id")  # 给所有的supplier都插入info
    # supplier_id = random.sample(cursor.fetchall() , n) #从已有的id中随机取出n个
    df_insert_info_supplier = pd.DataFrame(columns = ["supplier_id", "address_name", "nickname", "phone"])
    for i in range(len(supplier_id)):
        supplier_id_i = supplier_id[i]
        address_name = fake.address()
        nickname = fake.first_name()  # 生成收货昵称
        phone = fake.phone_number()
        insert_info_supplier = """
        INSERT INTO info_supplier(supplier_id, address_name, nickname, phone)
        values(:supplier_id,:address_name,:nickname,:phone)
        """
        df_insert_info_supplier.loc[i] = [supplier_id_i, address_name, nickname, phone]
        run_sql(insert_info_supplier, {"supplier_id": supplier_id_i,
                                       "address_name": address_name,
                                       "nickname": nickname,
                                       "phone": phone
                                       })
    df_insert_info_supplier.to_csv("../fake_data/insert_info_supplier.csv")


def insert_info_customer():
    get_id = """
    SELECT customer_id
    FROM customer
    """
    customer_id = get_col(run_sql(get_id), "customer_id")
    df_insert_info_customer = pd.DataFrame(columns = ["customer_id", "address_name", "nickname", "phone"])
    # customer_id = random.sample(cursor.fetchall(), n)
    for i in range(len(customer_id)):
        customer_id_i = customer_id[i]
        address_name = fake.address()
        nickname = fake.first_name()
        phone = fake.phone_number()
        insert_info_customer = """
        insert into info_customer(customer_id, address_name, nickname, phone)
        values(:customer_id,:address_name,:nickname,:phone)
        """
        df_insert_info_customer.loc[i] = [customer_id_i, address_name, nickname, phone]
        run_sql(insert_info_customer, {"customer_id": customer_id_i,
                                       "address_name": address_name,
                                       "nickname": nickname,
                                       "phone": phone})
    df_insert_info_customer.to_csv("../fake_data/insert_info_customer.csv")


def insert_product():
    product_info = pd.read_csv("product_info.csv", encoding = "GBK")
    product_name = product_info["商品名称"]
    pic_url = product_info["封面图链接"]
    price = product_info["价格"]
    get_number = """
    SELECT ISNULL(COUNT(*), 0) as number
    FROM product
    """
    number = get_col(run_sql(get_number), "number")

    get_id = """
    SELECT supplier_id
    FROM supplier
    """

    supplier_id = get_col(run_sql(get_id), "supplier_id")
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


def insert_cart():
    get_customer_id = """
        SELECT  customer_id
        FROM  customer
        """
    customer_id = get_col(run_sql(get_customer_id), "customer_id")

    get_product_id = """
    SELECT  product_id
    FROM  product
    """
    product_id = random.sample(get_col(run_sql(get_product_id), "product_id"), len(customer_id))
    df_insert_cart = pd.DataFrame(columns = ["customer_id", "product_id", "count"])
    for i in range(0, len(customer_id)):
        customer_id_i = customer_id[i]
        product_id_i = product_id[i]
        count = random.randint(0, 50)
        insert_cart = """
        INSERT INTO cart(customer_id , product_id, count)
        VALUES(:customer_id, :product_id, :count)
        """
        df_insert_cart.loc[i] = [customer_id_i, product_id_i, count]
        run_sql(insert_cart, {"customer_id": customer_id_i,
                              "product_id": product_id_i,
                              "count": count})
    df_insert_cart.to_csv("../fake_data/insert_cart.csv")


def insert_orders():
    get_number = """
    SELECT ISNULL(COUNT(*), 0) as number
    FROM orders
    """
    number = get_col(run_sql(get_number), "number")

    get_need_s = """
    SELECT s.supplier_id as supplier_id, p.product_id as product_id, p.price*(1-p.discount) as price
    FROM product p, supplier s
    WHERE s.supplier_id = p.supplier_id
    """
    need = run_sql(get_need_s)  # list类型

    get_customer_id = """
    SELECT customer_id
    FROM customer
    """
    need_customer_id = run_sql(get_customer_id)

    df_insert_orders = pd.DataFrame(columns = ["order_id", "customer_id", "supplier_id", "product_id", "orderdate",
                                               "quantity", "price_sum", "deliver_address", "receive_address",
                                               "is_return", "comment"])
    # 生成50*n条订单数据
    for i in range(50 * n):
        # 先查人对应的地址
        need_pro_inf = random.choice(need)
        supplier_id_i = need_pro_inf["supplier_id"] # 随机挑选1个,以下与他对应
        product_id_i = need_pro_inf["product_id"]
        price_unit_i = need_pro_inf["price"]
        customer_id_i = random.choice(get_col(need_customer_id, "customer_id"))
        get_address_c = """
        SELECT  address_name
        FROM  info_customer
        WHERE customer_id = '%s'
        """ % customer_id_i
        address_c = random.choice(get_col(run_sql(get_address_c), "address_name"))  # 只要一个地址就行

        get_address_s = """
        SELECT  address_name
        FROM  info_supplier
        WHERE supplier_id = '%s'
        """ % supplier_id_i
        address_s = random.choice(get_col(run_sql(get_address_s), "address_name"))

        order_id = 'O' + str(number[0] + i + 1).zfill(9)
        orderdate = fake.date_time_this_decade(before_now = True, after_now = False)  # 本年代中的日期
        quantity_i = random.randint(0, 50)
        price_sum = quantity_i * price_unit_i
        is_return = random.randint(0, 1)
        comment = fake.paragraph(nb_sentences = 2)[:100]

        insert_orders = """
        INSERT INTO orders(order_id, customer_id, supplier_id, product_id, orderdate, quantity, price_sum, deliver_address, receive_address, is_return, comment)
        VALUES(:order_id, :customer_id, :supplier_id, :product_id, :orderdate, :quantity, :price_sum, :deliver_address, :receive_address, :is_return, :comment)
        """
        df_insert_orders.loc[i] = [order_id, customer_id_i, supplier_id_i,
                                   product_id_i, orderdate, quantity_i, price_sum,
                                   address_s, address_c, is_return,
                                   comment]
        run_sql(insert_orders, {"order_id": order_id,
                                "customer_id": customer_id_i,
                                "supplier_id": supplier_id_i,
                                "product_id": product_id_i,
                                "orderdate": orderdate,
                                "quantity": quantity_i,
                                "price_sum": price_sum,
                                "deliver_address": address_s,
                                "receive_address": address_c,
                                "is_return": is_return,
                                "comment": comment})
        df_insert_orders.to_csv("../fake_data/insert_orders.csv")


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
