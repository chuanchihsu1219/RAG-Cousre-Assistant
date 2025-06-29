from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import supabase

import uuid

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = str(request.form.get("password"))

        # 檢查是否已存在
        existing = supabase.table("users").select("*").eq("email", email).execute().data
        if existing:
            flash("帳號已存在，請使用其他 Email 或登入。")
            return redirect(url_for("auth.register"))

        # 建立帳號
        hash_pw = generate_password_hash(password)
        user_id = str(uuid.uuid4())
        supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "password_hash": hash_pw
        }).execute()

        session["user_id"] = user_id
        session["email"] = email
        flash("註冊成功！")
        return redirect(url_for("chat.chat"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = str(request.form.get("password"))

        user_data = supabase.table("users").select("*").eq("email", email).execute().data
        if not user_data:
            flash("帳號不存在。請先註冊。")
            return redirect(url_for("auth.login"))

        user = user_data[0]
        if not check_password_hash(user["password_hash"], password):
            flash("密碼錯誤。請再試一次。")
            return redirect(url_for("auth.login"))

        session["user_id"] = user["id"]
        session["email"] = user["email"]
        flash("登入成功！")
        return redirect(url_for("chat.chat"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("已登出。")
    return redirect(url_for("auth.login"))
