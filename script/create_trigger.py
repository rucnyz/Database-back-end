import sys

sys.path.append(".")
from utils import run_sql

trig_insert_cart = """
    IF OBJECT_ID('trig_insert_cart','TR') IS NULL
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
                WHERE customer_id=@customer_id AND product_id=@product_id;
            END
    
            ELSE
            BEGIN
                INSERT cart
                SELECT * FROM inserted
            END
        END
    END;
    """

run_sql(trig_insert_cart)
