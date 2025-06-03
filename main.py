# main.py
from flask import Flask, redirect, url_for
from app.routes.chat import chat_bp
from app.routes.auth import auth_bp
from app.routes.schedule import schedule_bp
from app.utils.rag_chain import initialize_vectordb

app = Flask(__name__, template_folder="app/templates")
app.secret_key = "your_secret"

# 註冊所有藍圖（順序無關，但需明確 import）
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(schedule_bp)

initialize_vectordb()

@app.route("/")
def index():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True)
