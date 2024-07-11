from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('USER_DB')
password = os.getenv('PASSWORD_TO_USER')
host = os.getenv('HOST')
port = os.getenv('PORT')
database = os.getenv('DATABASE')

connection_str = \
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    posts = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    owners_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates='posts')


engine = create_engine(connection_str)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
