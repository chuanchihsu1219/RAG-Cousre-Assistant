# app/routes/auth.py
from fastapi import APIRouter, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import uuid
from config import supabase

router = APIRouter()

# 加密 & JWT 設定
SECRET_KEY = "your_secret_key" #Todo
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 天
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
def register(email: str = Form(...), password: str = Form(...)):
    existing = supabase.table("users").select("*").eq("email", email).execute().data
    if existing:
        raise HTTPException(status_code=400, detail="帳號已存在")

    user_id = str(uuid.uuid4())
    hashed_pw = pwd_context.hash(password)
    supabase.table("users").insert({"id": user_id, "email": email, "password_hash": hashed_pw}).execute()

    access_token = create_access_token(data={"sub": user_id})
    return JSONResponse({"access_token": access_token, "token_type": "bearer"})


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password

    user_data = supabase.table("users").select("*").eq("email", email).execute().data
    if not user_data:
        raise HTTPException(status_code=400, detail="帳號不存在")

    user = user_data[0]
    if not pwd_context.verify(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="密碼錯誤")

    access_token = create_access_token(data={"sub": user["id"]})
    return JSONResponse({"access_token": access_token, "token_type": "bearer"})

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="無效 token")
        return str(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="token 驗證失敗")
