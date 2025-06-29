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

    # 抓過往聊天紀錄（你可選擇是否實作從 DB 讀）
    chat_history = [] #Todo

    return templates.TemplateResponse("chat.html", {"request": request, "chat_history": chat_history, "selected_slots": selected})


@router.post("/chat")
async def chat_post(request: Request, user_input: str = Form(None), user_id: str = Depends(get_current_user)):  # 若為 JSON 請求此值為 None
    # 取得勾選的時段
    selected = []
    response = supabase.table("preferences").select("slots").eq("user_id", user_id).execute()
    if response.data:
        selected = response.data[0]["slots"]

    # 若為 JSON 請求（AJAX）
    if request.headers.get("content-type", "").startswith("application/json"):
        data = await request.json()
        user_input = data.get("user_input", "")

    # 推薦邏輯
    answer = recommend_course(user_input, selected)

    # 寫入聊天紀錄
    supabase.table("chat_history").insert({"user_id": user_id, "user_input": user_input, "bot_reply": answer, "used_slots": selected}).execute()

    # AJAX 回應
    if request.headers.get("content-type", "").startswith("application/json"):
        return JSONResponse({"answer": answer})

    # 表單回應 → 回傳單筆紀錄
    chat_history = [{"user": user_input, "bot": answer}]
    return templates.TemplateResponse("chat.html", {"request": request, "chat_history": chat_history, "selected_slots": selected})
