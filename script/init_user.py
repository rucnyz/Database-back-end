import sys

sys.path.append(".")
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

create_user_customer = """
    USE OnlineShopping;
    CREATE USER customer FROM LOGIN customer
"""

run_sql(create_user_customer)

create_user_supplier = """
    USE OnlineShopping;
    CREATE USER supplier FROM LOGIN supplier
"""

run_sql(create_user_supplier)

create_user_admin = """
    USE OnlineShopping;
    CREATE USER admin FROM LOGIN admin
"""

run_sql(create_user_admin)
