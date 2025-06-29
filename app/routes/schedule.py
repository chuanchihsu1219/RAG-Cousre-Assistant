# app/routes/schedule.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.routes.auth import get_current_user
from config import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/schedule")
async def get_schedule(request: Request, user_id: str = Depends(get_current_user)):
    response = supabase.table("preferences").select("slots").eq("user_id", user_id).execute()
    selected = response.data[0]["slots"] if response.data else []

    return templates.TemplateResponse("schedule.html", {"request": request, "selected_slots": selected})


@router.post("/schedule")
async def post_schedule(request: Request, timeslot: list[str] = Form(...), user_id: str = Depends(get_current_user)):
    payload: dict[str, list[str] | str] = {"slots": timeslot}
    response = supabase.table("preferences").select("id").eq("user_id", user_id).execute()

    if response.data:
        supabase.table("preferences").update(payload).eq("user_id", user_id).execute()
    else:
        payload["user_id"] = user_id
        supabase.table("preferences").insert(payload).execute()

    # 導回 GET /schedule
    return RedirectResponse("/schedule", status_code=303)


@router.post("/save_schedule")
async def save_schedule_json(request: Request, user_id: str = Depends(get_current_user)):
    try:
        data = await request.json()
        slots = data.get("slots", [])
        print("🔧 收到 slots:", slots)

        payload = {"slots": slots}
        response = supabase.table("preferences").select("user_id").eq("user_id", user_id).execute()

        if response.data:
            supabase.table("preferences").update(payload).eq("user_id", user_id).execute()
        else:
            payload["user_id"] = user_id
            supabase.table("preferences").insert(payload).execute()

        return JSONResponse({"success": True})

    except Exception as e:
        import traceback

        print("❌ 錯誤發生：", e)
        traceback.print_exc()
        return JSONResponse({"success": False, "message": "伺服器錯誤"}, status_code=500)
