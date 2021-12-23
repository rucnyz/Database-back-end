import sys

sys.path.append(".")
from utils import run_sql

use_db = """
USE OnlineShopping
            """
run_sql(use_db)

trig_insert_cart = """
    CREATE TRIGGER trig_insert_cart
    ON cart INSTEAD OF INSERT
    AS
    BEGIN
        DECLARE @customer_id char(10), @product_id char(10), @count int;
        SELECT @customer_id = customer_id, @product_id = product_id, @count = count FROM inserted;
        IF EXISTS(
        SELECT *
        FROM product
        WHERE product_id=@product_id AND remain>=@count
        )
            
        BEGIN
            IF EXISTS(
            SELECT *
            FROM cart
            WHERE customer_id=@customer_id AND product_id=@product_id)
                
            BEGIN
                UPDATE cart
                SET count=count+@count
                WHERE customer_id=@customer_id AND product_id=@product_id
            END
    
            ELSE
            BEGIN
                INSERT cart
                SELECT * FROM inserted
            END
        END
    END
    """

run_sql(trig_insert_cart)


trig_insert_orders_from_cart = """
    CREATE TRIGGER trig_insert_orders_from_cart
    ON orders INSTEAD OF INSERT
    AS
    BEGIN
        DECLARE @customer_id char(10), @product_id char(10), @quantity int;
        SELECT @customer_id=customer_id, @product_id=product_id, @quantity=quantity FROM inserted;
    
        IF EXISTS(
        SELECT *
        FROM product
        WHERE product_id=@product_id AND remain>=@quantity
        )
    
        BEGIN
            DELETE
            FROM cart
            WHERE customer_id=@customer_id AND product_id=@product_id AND count=@quantity
                
            UPDATE product
            SET remain=remain-@quantity
            WHERE product_id=@product_id
    
            INSERT INTO orders
            SELECT * FROM inserted
        END
    END
    """

run_sql(trig_insert_orders_from_cart)

trig_insert_customer = """
CREATE TRIGGER trig_insert_customer
ON customer INSTEAD OF INSERT
AS
BEGIN
    DECLARE @phone char(111);
    SELECT @phone=i.customer_phonenumber FROM inserted i;
    
    IF NOT EXISTS(
		SELECT *
		FROM customer c
		WHERE c.customer_phonenumber=@phone
		)
    
		BEGIN
			INSERT INTO customer
			SELECT * FROM inserted
		END
	ELSE RAISERROR('already exist', 12, 11)
END
"""
run_sql(trig_insert_customer)

# 一个表不能重复建立触发器
# trig_insert_orders_from_product = """
#     CREATE TRIGGER trig_insert_orders_from_product
#     ON orders INSTEAD OF INSERT
#     AS
#     BEGIN
#         DECLARE @customer_id char(10), @product_id char(10), @quantity int;
#         SELECT @customer_id=customer_id, @product_id=product_id, @quantity=quantity FROM inserted;
#
#         IF EXISTS(
#         SELECT *
#         FROM product
#         WHERE product_id=@product_id AND remain>=@quantity
#         )
#
#         BEGIN
#             UPDATE product
#             SET remain=remain-@quantity
#             WHERE product_id=@product_id
#
#             INSERT INTO orders
#             SELECT * FROM inserted
#         END
#     END
#     """
#
# run_sql(trig_insert_orders_from_product)
