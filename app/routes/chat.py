# app/routes/chat.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from app.utils.rag_chain import recommend_course
from config import supabase
from app.routes.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/chat")
async def chat_get(request: Request, user_id: str = Depends(get_current_user)):
    # 抓勾選的時段
    selected = []
    response = supabase.table("preferences").select("slots").eq("user_id", user_id).execute()
    if response.data:
        selected = response.data[0]["slots"]

    # 抓過往聊天紀錄
    chat_history = []
    response = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at").execute()
    if response.data:
        for chat in response.data:
            chat_history.append({"user": chat["user_input"], "bot": chat["bot_reply"]})

    return templates.TemplateResponse("chat.html", {"request": request, "chat_history": chat_history, "selected_slots": selected})


@router.post("/chat")
async def chat_post(request: Request, user_id: str = Depends(get_current_user)):
    # 取得勾選的時段
    selected = []
    response = supabase.table("preferences").select("slots").eq("user_id", user_id).execute()
    if response.data:
        selected = response.data[0]["slots"]

    # 獲取用戶輸入
    data = await request.json()
    user_input = data.get("user_input", "")

    # 如果有新的時段選擇，使用這些時段，否則使用從資料庫獲取的時段
    if "slots" in data and data["slots"]:
        selected = data["slots"]

    # 推薦邏輯
    answer = recommend_course(user_input, selected)

    # 寫入聊天紀錄
    supabase.table("chat_history").insert({"user_id": user_id, "user_input": user_input, "bot_reply": answer, "used_slots": selected}).execute()

    # 回傳 JSON 格式回應
    return JSONResponse({"answer": answer})
