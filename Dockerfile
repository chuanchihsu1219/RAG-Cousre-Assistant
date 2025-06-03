FROM python:3.11-slim

# 設定容器內工作目錄
WORKDIR /app

# 複製所有專案檔案進去
COPY . .

# 安裝套件
RUN pip install --no-cache-dir -r requirements.txt

# 啟動 Flask app，用 gunicorn
CMD ["gunicorn", "main:app"]
