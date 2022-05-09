from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from auth.db import database
from auth.models import users
from auth.settings import CLIENT_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRES_IN_THIS_MANY_MINUTES


class User(BaseModel):
    id: int
    username: str
    role: str
    email: Optional[str] = None


class DbUser(User):
    hashed_password: str


class Token(BaseModel):
    token_type: str
    access_token: str


class TokenData(BaseModel):
    username: Optional[str]



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


def get_password_hash(pwd: str):
    return pwd_context.hash(pwd)


async def get_user(username: str):
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)

    if not user:
        return None

    return DbUser(
        id=user.id,
        username=user.username,
        role=user.role,
        hashed_password=user.pwd_hash,
    )


def authenticate_user(user: DbUser, pwd: str) -> bool:
    if not verify_password(pwd, user.hashed_password):
        return False

    return True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, CLIENT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> DbUser:
    credentials_exception = HTTPException(status_code=401, detail='Invalid credentials', headers={'WWW-Authenticate': 'Bearer'})

    try:
        payload: dict = jwt.decode(token, key=CLIENT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    username = payload.get('sub')

    if username is None:
        raise credentials_exception

    token_data = TokenData(username=username)
    user = await get_user(username=token_data.username)  # type: ignore

    if user is None:
        raise credentials_exception

    return user


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


@app.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)

    if user is None:
        raise HTTPException(status_code=401, detail='Incorrect username or password', headers={'WWW-Authenticate': 'Bearer'})

    if not authenticate_user(user, form_data.password):
        raise HTTPException(status_code=401, detail='Incorrect username or password', headers={'WWW-Authenticate': 'Bearer'})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN_THIS_MANY_MINUTES)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/users/me')
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
