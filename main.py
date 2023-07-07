from fastapi import FastAPI, UploadFile, Form, Response,Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3
import jwt

con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

cur.execute(f"""
            create table IF NOT EXISTS items (
                id INTEGER primary key,
                title TEXT not null,
                image BLOB,
                price INTEGER not null,
                description TEXT,
                place TEXT not null,
                insertAt INTEGER not null 
            );
            """)

app = FastAPI()

SECRET = "super-coding"
manager = LoginManager(SECRET, '/login')


@manager.user_loader()
def query_user(data):
    WHERE_STATEMENTS = f'id="{data}"'
    if type(data) == dict:
        WHERE_STATEMENTS = f'id="{data["userid"]}"'
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user = cur.execute(f"""
                    SELECT * FROM users WHERE {WHERE_STATEMENTS}
                    """).fetchone()
    return user


@app.post('/login')
async def login(id: Annotated[str, Form()],
          password: Annotated[str, Form()], response:Response):
    user = query_user(id)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(data={
        'sub': {
            'name':user['name'],
            'email':user['email'],
            'userid':user['id']
        }
    })
    # 쿠키에 토큰 저장 로직 추가 -23.07.08
    cookie_token = jwt.encode({
            'name':user['name'],
            'email':user['email'],
            'userid':user['id']
        },SECRET,algorithm="HS256")
    response.set_cookie(key="access_token", value=cookie_token)
    
    return {"access_token":access_token}



@app.post('/signup')
def signup(id: Annotated[str, Form()],password: Annotated[str, Form()],name: Annotated[str, Form()],email: Annotated[str, Form()]):
    cur.execute(f"""
                INSERT INTO users(id,name,email,password)
                VALUES('{id}','{name}','{email}','{password}')
                """)
    con.commit()
    return '200'


@app.post('/items')
async def create_item(image: UploadFile,
                    title: Annotated[str, Form()],
                    price: Annotated[int, Form()],
                    description: Annotated[str, Form()],
                    place: Annotated[str, Form()],
                    insertAt: Annotated[int, Form()]
                    ):

    image_bytes = await image.read()
    cur.execute(f"""
                INSERT INTO 
                items(title,image,price,description,place,insertAt)
                VALUES('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
                """)
    con.commit()
    return '200'


@app.get('/items')
async def get_items(user=Depends(manager)):
    # 컬럼명도 같이 가져옴
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                    SELECT * from items;
                    """).fetchall()

    return JSONResponse(jsonable_encoder(dict(row) for row in rows))


@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0]

    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
