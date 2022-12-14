import logging
import os
from sqlalchemy import create_engine

uri = os.environ.get('DATABASE_URL')

if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

DATABASE_URL = uri

ENGINE = create_engine(DATABASE_URL, echo=True, future=True)