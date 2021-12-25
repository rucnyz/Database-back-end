from locust import FastHttpUser, task
from faker import Faker
import random

fake = Faker(locale='zh_CN')


class QuickstartUser(FastHttpUser):

    @task
    def home_page(self):
        cat = ['家用电器', '数码设备', '家居', '服装', '配饰', '美妆', '鞋类', '食品', '文娱', '其他']
        self.client.get("/api/HomePage/getProduct?needNumber=20&page=%s" % random.randint(1, 5))
        self.client.get("/api/HomePage/getCategory")
        cat.append("")
        self.client.post("/api/HomePage/getProductInCat",
                         json={"keywords": "美食",
                               "category": random.choice(cat),
                               "needNumber": 20,
                               "page": random.randint(1, 5)})



    @task
    def customer_info(self):
        self.client.post("/api/customer/login",
                         json={"phoneNumber": fake.phone_number(),
                               "password": fake.password(length=10)})
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/info")
        # 不需要用真实信息，给一个密码进数据库查询即可，错误就返回failed状态码
        self.client.post("/api/customer/C000000013/address/update",
                         json={"nickName": fake.name(),
                               "phoneNumber": fake.phone_number(),
                               "address": fake.address()})

    @task
    def customer_cart(self):
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/shoppingCart")
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/shoppingCart/add",
                         json={"productID": f"P{'{:0>9d}'.format(random.randint(1, 50))}",
                               "count": random.randint(0, 10)})
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/shoppingCart/update",
                         json={"productID": f"P{'{:0>9d}'.format(random.randint(1, 50))}",
                               "count": random.randint(0, 10)})
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/orders")
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/orders/add_cart",
                         json={"orders": [
                             {"productID": "P000000024", "orderDate": "2021-08-18 14:59:21.000", "priceSum": 111,
                              "quantity": 29, "receiveAddress": "黑龙江省宜都县梁平桂街d座 772017"}]})
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/orders/add_product",
                         json={"productID": "P000000001",
                               "orderDate": "2020-07-14 11:21:08",
                               "priceSum": 100,
                               "quantity": 10,
                               "receiveAddress": "somewhere1234"})
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1, 50))}/orders/get_address")

    @task
    def product(self):
        self.client.post(f"/api/product/P{'{:0>9d}'.format(random.randint(1, 100))}")


    @task
    def comment(self):
        self.client.post("/api/comment/update",
                         json={"orderID": f"O{'{:0>9d}'.format(random.randint(1, 100))}",
                               "comment": fake.sentence()})

    def admin(self):
        self.client.post("/api/admin/top3_product")
        self.client.post("/api/admin/province_top")
        self.client.post("/api/admin/top_product")
        self.client.post("/api/admin/annual_sales")
        self.client.post("/api/admin/province_top")




    # @task
    def hello_world(self):
        self.client.get("/")
