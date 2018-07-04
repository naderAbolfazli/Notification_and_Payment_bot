from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Config import Config

engine = create_engine(Config.database_url)
Session = sessionmaker(bind=engine)

Base = declarative_base()
