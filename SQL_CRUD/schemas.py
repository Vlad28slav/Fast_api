"""Modify standard list to more preferable form"""
from typing import List

from pydantic import BaseModel


class PostBase(BaseModel):
    """Creating base for creating post objects"""

    title: str
    content: str


class PostCreate(PostBase):
    """Creating a class to create posts, algorithm of creation is in main.py file"""

    pass


class Post(PostBase):
    """Objects post initialization"""

    id: int
    owners_id: int

    class Config:
        """Pydantic "ORM mode" is needed to enable the from_orm method
        in order to create a model instance by reading attributes from
        another class instance.
        """

        orm_mode = True


class UserBase(BaseModel):
    """Creating base for creating user objects"""

    name: str
    email: str


class UserCreate(UserBase):
    """Creating a class to create users, algorithm of creation is in main.py file"""

    pass


class User(UserBase):
    """Objects user initialization"""

    id: int
    posts: List[Post] = []

    class Config:
        """Pydantic "ORM mode" is needed to enable the from_orm method
        in order to create a model instance by reading attributes from
        another class instance.
        """

        orm_mode = True
