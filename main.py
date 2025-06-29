# main.py (FastAPI 版本)
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router
from app.routes.schedule import router as schedule_router
from app.utils.rag_chain import initialize_vectordb, recommend_course

# 建立 FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# 向量資料庫初始化
initialize_vectordb()

# 註冊 router（原本 Flask 的 blueprint）
# 設定明確的路徑前綴以避免路由衝突
app.include_router(auth_router, prefix="", tags=["auth"])
app.include_router(chat_router, prefix="", tags=["chat"])
app.include_router(schedule_router, prefix="", tags=["schedule"])


# 首頁導向登入
@app.get("/")
def index():
    return RedirectResponse(url="/login")


# ping 測試向量庫
@app.get("/ping")
def ping():
    print("📥 Ping 被呼叫，測試向量庫")
    recommend_course("英文", ["2_2", "2_3", "2_4"])
    return {"status": "ok"}
