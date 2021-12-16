import sys
sys.path.append(".")
from utils import run_sql

del_database = """  
    commit;
    USE master;
    DROP DATABASE OnlineShopping;
"""

run_sql(del_database)