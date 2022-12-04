from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
import psycopg2
from fastapi.security import OAuth2PasswordRequestForm
from psycopg2.extras import RealDictCursor
from starlette import status

import oauth2
from JWT import create_access_token
from schemas import *
from hashing import bcrypt, verify_password

app = FastAPI()

try:
    conn = psycopg2.connect(
        user='postgres',
        password=123,
        database='fastapi',
        cursor_factory=RealDictCursor
    )

    conn.autocommit = True
except Exception as ex:
    print(ex)


@app.get('/posts/')
def get_posts():
    with conn.cursor() as cursor:
        cursor.execute(
            '''
            SELECT * FROM items
            '''
        )
        items = cursor.fetchall()
        return items


@app.get('/posts/{post_id}/')
def get_post(post_id: int, current_user: User = Depends(oauth2.get_current_user)):
    with conn.cursor() as cursor:
        cursor.execute(
            f'''
            SELECT * FROM items WHERE id = {post_id}
            '''
        )
        item = cursor.fetchall()
        return item


@app.post('/posts/')
def create_post(post: Items):
    with conn.cursor() as cursor:
        cursor.execute(
            '''insert into items (title, text, date_created,category_id) values (%s,%s,%s,%s)''',
            (post.title, post.text, datetime.now(), None)
        )
        # items = cursor.fetchall()
        return {"msg": "created"}


@app.delete('/posts/post_id}/')
def delete_post(post_id: int):
    with conn.cursor() as cursor:
        cursor.execute(
            f'''DELETE from items 
            WHERE id = {post_id}''',

        )
        return {"msg": "deleted"}


@app.put('/posts/post_id}/')
def update_post(post_id: int, post: Items):
    with conn.cursor() as cursor:
        cursor.execute(
            f'''UPDATE items 
            SET title = '{post.title}', text = '{post.text}', category_id = '{post.category_id}'  
            where id = {post_id}'''

        )
        return {"msg": "updated"}


@app.post('/register/')
def register(data: User):
    with conn.cursor() as cursor:
        cursor.execute(
            '''insert into users (name, password) values (%s,%s)''',
            (data.name, bcrypt(data.password))
        )
        return {"msg": "created"}


@app.get('/users/')
def get_users():
    with conn.cursor() as cursor:
        cursor.execute(
            '''SELECT * from users'''
        )
        users = cursor.fetchall()
        return users


@app.post('/login/')
def login(data: OAuth2PasswordRequestForm = Depends()):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT * FROM users 
            WHERE name = '{data.username}'"""
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='invalid username')
        if not verify_password(data.password, dict(user).get('password')):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='invalid password')

        access_token = create_access_token(
            data={"sub": dict(user).get('name')}
        )
        return {"access_token": access_token, "token_type": "bearer"}
