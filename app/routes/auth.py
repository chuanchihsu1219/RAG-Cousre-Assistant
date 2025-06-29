# app/routes/auth.py
from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import uuid
import logging
import sys
from config import supabase

# 設定日誌系統
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("auth_routes")

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

# 加密 & JWT 設定
SECRET_KEY = "your_secret_key"  # Todo
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
    try:
        existing = supabase.table("users").select("*").eq("email", email).execute().data
        if existing:
            raise HTTPException(status_code=400, detail="帳號已存在")

        user_id = str(uuid.uuid4())
        hashed_pw = pwd_context.hash(password)

        logger.info(f"嘗試註冊新用戶: {email}")
        supabase.table("users").insert({"id": user_id, "email": email, "password_hash": hashed_pw}).execute()
        logger.info(f"用戶註冊成功: {email} / {user_id}")

        # 生成訪問 token
        access_token = create_access_token(data={"sub": user_id})
        logger.info(f"用戶 {user_id} 註冊成功，生成訪問令牌")

        # 設定 cookie 和重定向到聊天頁面
        response = RedirectResponse(url="/chat", status_code=303)

        # 設置多種 cookie 格式以增加兼容性
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="lax", max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        # 另外設置一個純 token cookie，某些客戶端可能需要
        response.set_cookie(key="token", value=access_token, httponly=True, samesite="lax", max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        logger.info("已設置身份認證 cookie 並重定向到聊天頁面")
        return response
    except Exception as e:
        # 捕捉並記錄所有例外
        logger.error(f"註冊過程發生錯誤: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status_code=500, detail="註冊失敗，請稍後再試")


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password

    logger.info(f"嘗試登入: {email}")

    try:
        user_data = supabase.table("users").select("*").eq("email", email).execute().data
        if not user_data:
            logger.warning(f"登入失敗: 帳號 {email} 不存在")
            raise HTTPException(status_code=400, detail="帳號不存在")
    except Exception as e:
        logger.error(f"查詢用戶資料時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="登入過程發生錯誤，請稍後再試")

    user = user_data[0]

    try:
        if not pwd_context.verify(password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="密碼錯誤")
    except Exception as e:
        from passlib.exc import UnknownHashError

        # 特別處理無法識別的密碼雜湊格式
        if isinstance(e, UnknownHashError) or "hash could not be identified" in str(e):
            logger.error(f"密碼雜湊無法識別: {str(e)}")
            # 嘗試重新設定密碼雜湊
            try:
                hashed_pw = pwd_context.hash(password)
                supabase.table("users").update({"password_hash": hashed_pw}).eq("id", user["id"]).execute()
                # 更新成功，繼續登入流程
                logger.info(f"已自動修復用戶 {user['id']} 的密碼雜湊")
            except Exception as update_err:
                logger.error(f"修復密碼雜湊失敗: {str(update_err)}")
                logger.error(f"用戶資料: {user['id']} / {user['email']}")
                raise HTTPException(status_code=500, detail="密碼驗證錯誤，請聯絡系統管理員")
        else:
            # 其他未預期的錯誤
            logger.error(f"密碼驗證發生未知錯誤: {str(e)}")
            logger.error(f"用戶資料: {user['id']} / {user['email']}")
            raise HTTPException(status_code=500, detail="登入過程發生錯誤，請稍後再試")

    # 生成訪問 token
    access_token = create_access_token(data={"sub": user["id"]})
    logger.info(f"用戶 {user['id']} 登入成功，生成訪問令牌")

    # 設定 cookie 和 session
    response = RedirectResponse(url="/chat", status_code=303)

    # 設置多種 cookie 格式以增加兼容性
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="lax", max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    # 另外設置一個純 token cookie，某些客戶端可能需要
    response.set_cookie(key="token", value=access_token, httponly=True, samesite="lax", max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    logger.info("已設置身份認證 cookie 並重定向到聊天頁面")
    return response


from fastapi import Cookie, Header
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# 使用正確的 tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 自訂 token 獲取函數，支援從 cookie 中讀取 token
security = HTTPBearer()


async def get_token_from_cookie_or_header(authorization: Optional[str] = Header(None), access_token: Optional[str] = Cookie(None)):
    # 嘗試從 header 或 cookie 中獲取 token
    if authorization:
        return authorization.split(" ")[1]
    elif access_token and access_token.startswith("Bearer "):
        return access_token.split(" ")[1]
    elif access_token:  # 純 token 無 Bearer 前綴
        return access_token
    return None


def get_current_user(token: Optional[str] = Depends(get_token_from_cookie_or_header)) -> str:
    if token is None:
        logger.error("無法獲取 Token: 請求中沒有提供授權信息")
        raise HTTPException(
            status_code=401,
            detail="未提供認證信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        logger.info(f"驗證用戶 Token: {token[:10]}...")  # 只記錄前10個字元，保護隱私
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning("Token 無效: sub 欄位不存在")
            raise HTTPException(status_code=401, detail="無效 token")
        logger.info(f"用戶 {user_id} 成功通過驗證")
        return str(user_id)
    except JWTError as e:
        logger.error(f"Token 驗證失敗: {str(e)}")
        raise HTTPException(status_code=401, detail="token 驗證失敗")
    except Exception as e:
        logger.error(f"Token 處理過程中發生未知錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="伺服器錯誤")


@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/auth-status")
async def auth_status(user_id: Optional[str] = Depends(get_current_user)):
    """檢查當前認證狀態，對調試很有幫助"""
    if user_id:
        return {"status": "authenticated", "user_id": user_id}
    return {"status": "not authenticated"}
