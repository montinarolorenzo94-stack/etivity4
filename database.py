# database.py
# ---------------------------------------------------------------------
# IN QUESTO FILE DEFINIAMO LE REGOLE PER CONNETTERCI AL DATABASE
# ---------------------------------------------------------------------
#

import os
from sqlalchemy import create_engine

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "password") # password originale nascosta
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "CentroRiparazioni")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
