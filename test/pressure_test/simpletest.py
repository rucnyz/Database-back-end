from locust import FastHttpUser, task
import random


class QuickstartUser(FastHttpUser):

    @task
    def home_page(self):
        self.client.get("/api/HomePage/getProduct?needNumber=20&page=1")
        self.client.get("/api/HomePage/getCategory")

    @task
    def customer_info(self):
        self.client.post(f"/api/customer/C{'{:0>9d}'.format(random.randint(1,50))}/info")

    # @task
    def hello_world(self):
        self.client.get("/")
