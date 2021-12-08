import sys
import random
from utils import run_sql
from faker import Faker

sys.path.append(".")

fake = Faker(locale='zh_CN')

n = 50  # 生成的数据数量

def insert_customer():
    get_number = """
    SELECT ISNULL(COUNT(*),0)
    FROM customer
    """
    cursor.execute(get_number)
    number = cursor.fetchall()  # 数值型

    for i in range(n):
        password_temp = fake.password(length=10, upper_case=True, lower_case=True)
        insert_customer = """"
        insert into customer(customer_id, customer_phonenumber, customer_password)
        values('%s','%s','%s')
        """ % ('C' + str(number + i + 1),  # 编号
               fake.phone_number(),
               hashlib.sha256(password_temp).hexdigest())
        cursor.execute(insert_customer)


def insert_supplier():
    get_number = """
    SELECT ISNULL(COUNT(*),0)
    FROM supplier
    """
    cursor.execute(get_number)
    number = cursor.fetchall()
    for i in range(n):
        password_temp = fake.password(length=10, upper_case=True, lower_case=True)
        insert_supplier = """"
        insert into info_supplier(supplier_id, supplier_password, supplier_name, owner_name, owner_id)
        values('%s','%s','%s','%s','%s')
        """ % ('S' + str(number + i + 1),
               hashlib.sha256(password_temp).hexdigest(),
               fake.company(),  # supplier_name是店铺名称
               fake.name(),
               fake.ssn(min_age=18, max_age=90))  # owner_id 是店铺主的身份证号
        cursor.execute(insert_supplier)


def insert_info_supplier():
    get_id = """
    SELECT supplier_id
    FROM supplier
    """
    cursor.execute(get_id)
    supplier_id = cursor.fetchall()  # 给所有的supplier都插入info
    # supplier_id = random.sample(cursor.fetchall() , n) #从已有的id中随机取出n个
    for i in range(len(supplier_id)):
        insert_info_supplier = """"
        insert into info_supplier(supplier_id, address_name, nickname, phone)
        values('%s','%s','%s','%s')
        """ % (supplier_id[i],
               fake.address(),
               fake.first_name(),  # 生成收货昵称
               fake.phone_number())
        cursor.execute(insert_info_supplier)


def insert_info_customer():
    get_id = """
    SELECT customer_id
    FROM customer
    """
    cursor.execute(get_id)
    customer_id = cursor.fetchall()
    # customer_id = random.sample(cursor.fetchall(), n)
    for i in range(len(customer_id)):
        insert_info_customer = """"
        insert into info_customer(customer_id, address_name, nickname, phone)
        values('%s','%s','%s','%s')
        """ % (customer_id[i],
               fake.address(),
               fake.first_name(),  # 随机生成收货昵称
               fake.phone_number())
        cursor.execute(insert_info_customer)


def insert_product():
    get_number = """
    SELECT ISNULL(COUNT(*), 0)
    FROM product
    """
    cursor.execute(get_number)
    number = cursor.fetchall()

    get_id = """
    SELECT supplier_id
    FROM supplier
    """
    cursor.execute(get_id)
    supplier_id = cursor.fetchall()
    # supplier_id = random.sample(cursor.fetchall(), n)
    for i in range(len(supplier_id)):
        insert_product = """
        INSERT INTO product(product_id, product_name, price, supplier_id, remain, size, discount, category, pic_url)
        values('%s','%s','%u','%s','%u','%s','%f','%s','%s')
        """ % ('P' + str(number + i + 1),  # 编号
               fake.word(),  # TODO product_name 现在就是随便生成一个词
               random.randint(0, 9999999),
               supplier_id[i],
               random.randint(0, 9999999),
               fake.word(ext_word_list=['S', 'M', 'L', 'XL']),  #尺寸SML XL
               round(random.random(), 2),
               fake.word(),  # TODO category 现在是随便生成一个词
               fake.image_url(width=None, height=None))
        cursor.execute(insert_product)


def insert_orders():
    get_number = """
    SELECT ISNULL(COUNT(*), 0)
    FROM product
    """
    cursor.execute(get_number)
    number = cursor.fetchall()

    get_need_sp = """
    SELECT s.supplier_id, p.product_id, p.price*(1-p.discount)
    FROM product p supplier s, 
    WHERE s.supplier_id = p.supplier_id
    """
    cursor.execute(get_need_sp)
    need = cursor.fetchall()  # list类型
    supplier_id = random.sample([x[0] for x in need], n)  # 随机挑选n个
    product_id = random.sample([x[1] for x in need], n)
    price_unit = random.sample([x[2] for x in need], n)

    get_customer_id = """
    SELECT customer_id
    FROM customer
    """
    cursor.execute(get_customer_id)
    customer_id = random.sample([x[1] for x in need], n)

    quantity = [random.randint(0, 9999) for x in range(n)]

    for i in range(n):
        # 先查人对应的地址
        get_address_c = """
        SELECT  address_name
        FROM  info_customer
        WHERE customer_id = %s
        """ % customer_id[i]
        cursor.execute(get_address_c)
        address_c = cursor.fetchone()  # 只要一个地址就行

        get_address_s = """
        SELECT  address_name
        FROM  info_supplier
        WHERE ifc.supplier_id = %s
        """ % supplier_id[i]
        cursor.execute(get_address_s)
        address_s = cursor.fetchone()

        insert_orders = """
        INSERT INTO orders(order_id, customer_id, supplier_id, product_id, orderdate, quantity, price_sum, deliver_address, receive_address, is_return, comment)
        VALUES('%s','%s','%s','%s','%s','%u','%f','%s','%s','%u','%s')
        """ % ('O' + str(number + i + 1),
               customer_id[i],
               supplier_id[i],
               product_id[i],
               fake.date_this_decade(before_today=True, after_today=False),  # 本年代中的日期
               quantity[i],
               quantity[i] * price_unit[i],
               address_s,
               address_c,
               random.randint(0, 1),
               fake.paragraph(nb_sentences=2)[:100]  # varchar(200)
               )
        cursor.execute(insert_product)


def insert_cart():
    get_customer_id = """
        SELECT  customer_id
        FROM  customer
        """
    cursor.execute(get_customer_id)
    customer_id = cursor.fetchall()

    get_product_id = """
    SELECT  product_id
    FROM  product
    """
    cursor.execute(get_product_id)
    product_id = random.sample(cursor.fetchall(), len(customer_id))

    for i in range(0, len(customer_id)):
        insert_cart = """
        INSERT INTO cart(customer_id , product_id, count)
        VALUES(%s,%s,%u)
        """ % (customer_id[i],
               product_id[i],
               random.randint(0, 9999)
               )
        cursor.execute(insert_cart)


def insert_fake():
    insert_customer()
    insert_supplier()
    insert_info_customer()
    insert_info_supplier()
    insert_product()
    insert_product()
    insert_cart()

insert_fake()  # 执行所有插入
# cursor.close()
# conn.close()
