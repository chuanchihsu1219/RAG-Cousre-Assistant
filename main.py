from flask import Flask
from app.routes.chat import chat_bp

app = Flask(__name__)
app.secret_key = "your_secret"

app.register_blueprint(chat_bp)

from app.routes.schedule import schedule_bp
app.register_blueprint(schedule_bp)


if __name__ == "__main__":
    app.run(debug=True)
