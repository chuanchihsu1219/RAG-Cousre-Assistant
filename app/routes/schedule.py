from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import supabase

schedule_bp = Blueprint("schedule", __name__)

@schedule_bp.route("/schedule", methods=["GET", "POST"])
def schedule():
    user_id = session.get("user_id")
    if not user_id:
        flash("請先登入")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        selected = request.form.getlist("timeslot")
        session["schedule"] = selected

        # 儲存進 Supabase
        existing = supabase.table("preferences").select("*").eq("user_id", user_id).execute().data
        if existing:
            supabase.table("preferences").update({"slots": selected}).eq("user_id", user_id).execute()
        else:
            supabase.table("preferences").insert({"user_id": user_id, "slots": selected}).execute()
        flash("時間已儲存！")

    else:
        # 若尚未設定則從 Supabase 載入
        record = supabase.table("preferences").select("slots").eq("user_id", user_id).execute().data
        selected = record[0]["slots"] if record else []
        session["schedule"] = selected

    return render_template("schedule.html", selected_slots=selected)
