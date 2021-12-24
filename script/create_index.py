import sys

sys.path.append(".")
from utils import run_sql

use_db = """
USE OnlineShopping
            """
run_sql(use_db)

index_ = """
    CREATE UNIQUE INDEX
    ON 
"""