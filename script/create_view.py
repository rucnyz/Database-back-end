import sys

sys.path.append(".")
from utils import run_sql

use_db = """
USE OnlineShopping
            """
run_sql(use_db)

# 每个商家每个用户消费额
sum_consume_eachsupp_eachcust = """
    CREATE VIEW SUM_CONSUME_EACHSUPP_EACHCUST
    AS
    SELECT o.supplier_id, supplier_name, customer_id, round(SUM(price_sum),2) sum_consume
    FROM supplier s, orders o
    WHERE s.supplier_id=o.supplier_id
    GROUP BY o.supplier_id, supplier_name, customer_id
"""

run_sql(sum_consume_eachsupp_eachcust)

# 每个商家每个商品的销量
sum_quantity = """
    CREATE VIEW SUM_QUANTITY
    AS
    SELECT o.product_id, product_name, o.supplier_id, supplier_name, SUM(quantity) sum_quantity
    FROM orders o, supplier s, product p
    WHERE s.supplier_id=o.supplier_id AND p.product_id=o.product_id
    GROUP BY o.supplier_id, supplier_name, o.product_id, product_name
"""

run_sql(sum_quantity)

# 每个会员购买各商品数量
sum_quantity_eachcust_eachpro = """
    CREATE VIEW SUM_QUANTITY_EACHCUST_EACHPRO
    AS
    SELECT o.customer_id, p.product_id, product_name, SUM(quantity) sum_quantity
    FROM orders o, product p
    WHERE o.product_id = p.product_id
    GROUP BY o.customer_id, p.product_id, product_name
"""

run_sql(sum_quantity_eachcust_eachpro)

# run_sql("DROP VIEW SUM_QUANTITY")
# run_sql("DROP VIEW sum_consume_eachsupp_eachcust")
# run_sql("DROP VIEW SUM_QUANTITY_EACHCUST_EACHPRO")
