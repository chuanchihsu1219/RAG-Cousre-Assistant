# app/routes/chat.py
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from config import supabase
from app.utils.rag_chain import recommend_course

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        flash("請先登入")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    chat_history = session.get("chat_history", [])

    # 讀取 schedule（供 checkbox 回填）
    selected = []
    response = supabase.table("preferences").select("slots").eq("user_id", user_id).execute()
    if response.data:
        selected = response.data[0]["slots"]
        session["schedule"] = selected

    if request.method == "POST":
        # 若是 JSON 請求（AJAX）
        if request.is_json:
            data = request.get_json()
            user_input = data.get("user_input", "")
            schedule = session.get("schedule", [])
            answer = recommend_course(user_input, schedule)

            supabase.table("chat_history").insert({
                "user_id": user_id,
                "user_input": user_input,
                "bot_reply": answer,
                "used_slots": schedule
            }).execute()

            chat_history.append({"user": user_input, "bot": answer})
            session["chat_history"] = chat_history

            return jsonify({"answer": answer})

        # 否則為一般表單提交
        user_input = request.form.get("user_input", "")
        schedule = session.get("schedule", [])

        answer = recommend_course(user_input, schedule)

        supabase.table("chat_history").insert({
            "user_id": user_id,
            "user_input": user_input,
            "bot_reply": answer,
            "used_slots": schedule
        }).execute()

        chat_history.append({"user": user_input, "bot": answer})
        session["chat_history"] = chat_history

    return render_template("chat.html", chat_history=chat_history, selected_slots=selected)
