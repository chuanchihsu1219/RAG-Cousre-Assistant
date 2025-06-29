# app/routes/schedule.py
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

        payload = {"slots": selected}
        response = supabase.table("preferences").select("id").eq("user_id", user_id).execute()

        if response.data:
            supabase.table("preferences").update(payload).eq("user_id", user_id).execute()
        else:
            payload["user_id"] = user_id
            supabase.table("preferences").insert(payload).execute()

        flash("時間偏好已儲存！")
        return redirect(url_for("schedule.schedule"))  # ← ★ Redirect 回 GET！

    else:
        response = supabase.table("preferences").select("slots").eq("user_id", user_id).execute()
        selected = response.data[0]["slots"] if response.data else []
        session["schedule"] = selected
    import inspect
    print("🔍 使用中的 schedule.html 來源：", inspect.getfile(inspect.currentframe()))

    return render_template("schedule.html", selected_slots=selected)

from flask import jsonify, request, session
import traceback

@schedule_bp.route("/save_schedule", methods=["POST"])
def save_schedule():
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify(success=False, message="未登入"), 401

        slots = request.json.get("slots", [])
        print("🔧 收到 slots:", slots)

        payload = {"slots": slots}
        response = supabase.table("preferences").select("user_id").eq("user_id", user_id).execute()

        if response.data:
            supabase.table("preferences").update(payload).eq("user_id", user_id).execute()
        else:
            payload["user_id"] = user_id
            supabase.table("preferences").insert(payload).execute()

        session["schedule"] = slots
        return jsonify(success=True)

    except Exception as e:
        import traceback
        print("❌ 錯誤發生：", e)
        traceback.print_exc()
        return jsonify(success=False, message="伺服器錯誤"), 500


