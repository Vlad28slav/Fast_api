"""Import os to use .getenv function"""
import os

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")

connection_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
Base = declarative_base()


class User(Base):
    """Definition of a User object"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    posts = relationship("Post", back_populates="owner")


class Post(Base):
    """Definition of a Post object"""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    owners_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")


engine = create_engine(connection_str)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
