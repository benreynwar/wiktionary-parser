"""
Takes care of setting up the database for wiktionary_parser.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://myusername:mypassword@/wiktionary_parser", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
