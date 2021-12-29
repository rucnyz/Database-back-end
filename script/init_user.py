import sys

sys.path.append("..")
from utils import run_sql

create_login_customer = """
    USE OnlineShopping;
    CREATE LOGIN customer WITH PASSWORD = 'PasswordForCustomer',
    CHECK_POLICY = OFF;
"""

run_sql(create_login_customer)

create_login_supplier = """
    USE OnlineShopping;
    CREATE LOGIN supplier WITH PASSWORD = 'PasswordForSupplier',
    CHECK_POLICY = OFF;
"""

run_sql(create_login_supplier)

create_login_admin = """
    USE OnlineShopping;
    CREATE LOGIN admin WITH PASSWORD = 'PasswordForAdmin',
    CHECK_POLICY = OFF;
"""

run_sql(create_login_admin)
#创建角色并进行权限赋予。
create_user_customer = """
    USE OnlineShopping;
    CREATE USER customer FROM LOGIN customer   
    
"""
run_sql(create_user_customer)

grant_customer_1 = """
    GRANT ALL PRIVILEGES
    ON customer
    TO customer;
    
    GRANT ALL PRIVILEGES
    ON info_customer
    TO customer;
    
    GRANT ALL PRIVILEGES
    ON orders
    TO customer;
    
    GRANT ALL PRIVILEGES
    ON  cart
    TO customer;
"""
run_sql(grant_customer_1)

grant_customer_2 = """
    GRANT SELECT, UPDATE
    ON product
    TO customer

"""
run_sql(grant_customer_2)
#商家注册
create_user_supplier = """
    USE OnlineShopping;
    CREATE USER supplier FROM LOGIN supplier
    
"""
run_sql(create_user_supplier)

grant_supplier_1 = """
    GRANT ALL PRIVILEGES
    ON supplier
    TO supplier;
    
    GRANT ALL PRIVILEGES
    ON info_supplier
    TO supplier;
    
    GRANT ALL PRIVILEGES
    ON product
    TO supplier;
"""
grant_supplier_2 = """
    GRANT SELECT
    ON orders
    TO supplier
"""
run_sql(grant_supplier_1)
run_sql(grant_supplier_2)

#管理员
create_user_admin = """
    USE OnlineShopping;
    CREATE USER admin FROM LOGIN admin
    
"""
run_sql(create_user_admin)

grant_admin = """
    GRANT ALL PRIVILEGES
    ON supplier
    TO admin
    WITH GRANT OPTION;
    
    GRANT ALL PRIVILEGES
    ON customer
    TO admin
    WITH GRANT OPTION;
    
    GRANT ALL PRIVILEGES
    ON info_customer
    TO admin
    WITH GRANT OPTION;
    
    GRANT ALL PRIVILEGES
    ON info_supplier
    TO admin
    WITH GRANT OPTION;

    GRANT ALL PRIVILEGES
    ON product
    TO admin
    WITH GRANT OPTION;
    
    GRANT ALL PRIVILEGES
    ON orders
    TO admin
    WITH GRANT OPTION;
    
    GRANT ALL PRIVILEGES
    ON cart
    TO admin
    WITH GRANT OPTION;
    
    GRANT ALL PRIVILEGES
    ON  admin
    TO admin
    WITH GRANT OPTION;




"""
run_sql(grant_admin)