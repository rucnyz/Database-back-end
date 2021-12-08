import sys
sys.path.append(".")
from utils import run_sql

create_customer = """
    CREATE LOGIN customer WITH PASSWORD = 'PasswordForCustomer',
    CHECK_POLICY = OFF;
"""

run_sql(create_customer)

create_supplier = """
    CREATE LOGIN supplier WITH PASSWORD = 'PasswordForSupplier',
    CHECK_POLICY = OFF;
"""

run_sql(create_supplier)

create_admin = """
    CREATE LOGIN admin WITH PASSWORD = 'PasswordForAdmin',
    CHECK_POLICY = OFF;
"""

run_sql(create_admin)