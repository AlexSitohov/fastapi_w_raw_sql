from datetime import date

from pydantic import BaseModel


class Items(BaseModel):
    id: int
    title: str
    text: str
    date_created: date
    category_id: int


class User(BaseModel):
    name: str
    password: str


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None