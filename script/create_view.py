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
SELECT o.supplier_id, supplier_name, o.customer_id, c.customer_nickname, round(SUM(price_sum), 2) sum_consume
FROM supplier s,
     orders o,
     customer c
WHERE s.supplier_id = o.supplier_id
  AND o.customer_id = c.customer_id
GROUP BY o.supplier_id, supplier_name, o.customer_id, customer_nickname
"""

run_sql(sum_consume_eachsupp_eachcust)

# 每个商家每个商品的销量
sum_quantity = """
    CREATE VIEW SUM_QUANTITY
    AS
        SELECT  p.supplier_id, supplier_name, p.product_id, p.product_name, ISNULL(sub.sales, 0) sum_quantity
        FROM product p
        INNER JOIN supplier s ON  s.supplier_id =p.supplier_id
        LEFT JOIN(
            SELECT orders.product_id, sum(orders.quantity) sales
            FROM product, orders
            WHERE product.product_id=orders.product_id
            GROUP BY orders.product_id
            ) sub
            ON p.product_id=sub.product_id


"""

run_sql(sum_quantity)

# 每个会员购买各商品数量
sum_quantity_eachcust_eachpro = """
CREATE VIEW SUM_QUANTITY_EACHCUST_EACHPRO
AS
SELECT o.customer_id, customer_nickname, p.product_id, product_name, SUM(quantity) sum_quantity
FROM orders o,
     product p,
     customer c
WHERE o.product_id = p.product_id
  AND o.customer_id = c.customer_id
GROUP BY o.customer_id, p.product_id, product_name, customer_nickname
"""

run_sql(sum_quantity_eachcust_eachpro)

# run_sql("DROP VIEW SUM_QUANTITY")
# run_sql("DROP VIEW SUM_CONSUME_EACHSUPP_EACHCUST")
# run_sql("DROP VIEW SUM_QUANTITY_EACHCUST_EACHPRO")
