from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from config import supabase
from app.utils.rag_chain import recommend_course  # 新增這一行

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        flash("請先登入")
        return redirect(url_for("auth.login"))

    chat_history = []
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        schedule = session.get("schedule", [])  # 現在 schedule 仍然不作用，但可以日後整合 metadata

        # 呼叫 LangChain-based RAG 系統進行推薦
        answer = recommend_course(user_input, schedule)

        # 儲存聊天紀錄
        supabase.table("chat_history").insert({
            "user_id": session["user_id"],
            "user_input": user_input,
            "bot_reply": answer,
            "used_slots": schedule
        }).execute()

        chat_history.append({"user": user_input, "bot": answer})

    return render_template("chat.html", chat_history=chat_history)
