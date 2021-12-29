import sys
sys.path.append("..")
from utils import run_sql


use_db = """
USE OnlineShopping
            """
run_sql(use_db)

index_customer = """
    CREATE UNIQUE INDEX cusID
    ON customer(customer_id)
"""
run_sql(index_customer)

index_supplier = """
    CREATE UNIQUE INDEX suppID
    ON supplier(supplier_id)
"""
run_sql(index_supplier)

index_custInfo = """
    CREATE UNIQUE INDEX custinfoID
    ON info_customer(customer_id)
"""
run_sql(index_custInfo)

index_suppInfo = """
    CREATE UNIQUE INDEX suppinfoID
    ON info_supplier(supplier_id)
"""
run_sql(index_suppInfo)

index_product = """
    CREATE UNIQUE INDEX productID
    ON product(product_id)
"""
run_sql(index_product)

index_orders = """
    CREATE UNIQUE INDEX ordersID
    ON orders(order_id)
"""
run_sql(index_orders)

index_cart = """
    CREATE UNIQUE INDEX cartIndex
    ON cart(customer_id,product_id)
"""
run_sql(index_cart)

index_admin = """
    CREATE UNIQUE INDEX adminID
    ON admin(admin_id)
"""
run_sql(index_admin)

index_product_order = """
    CREATE INDEX index_ordertime ON orders(orderdate)
    CREATE INDEX index_product ON product(product_name)
"""
run_sql(index_product_order)