from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import supabase

schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule", methods=["GET", "POST"])
def schedule():
    user_id = session.get("user_id")
    if not user_id:
        flash("請先登入")
        return redirect(url_for("auth.login"))

    selected = []

    if request.method == "POST":
        selected = request.form.getlist("timeslot")
        session["schedule"] = selected

        # 確保資料為 JSON 陣列格式
        payload = {"slots": selected}

        # 儲存進 Supabase（update or insert）
        response = supabase.table("preferences").select("id").eq("user_id", user_id).execute()
        if response.data:
            supabase.table("preferences").update(payload).eq("user_id", user_id).execute()
        else:
            payload["user_id"] = user_id
            supabase.table("preferences").insert(payload).execute()

        flash("時間偏好已儲存！")

    else:
        # 初次進入頁面時載入既有偏好（若有）
        response = supabase.table("preferences").select("slots").eq("user_id", user_id).execute()
        selected = response.data[0]["slots"] if response.data else []
        session["schedule"] = selected

    return render_template("schedule.html", selected_slots=selected)
