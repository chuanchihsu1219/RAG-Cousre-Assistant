FROM python:3.11-slim-bookworm

# 更新系統套件以減少漏洞
RUN apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y && apt-get install --only-upgrade python3 && apt-get clean && rm -rf /var/lib/apt/lists/*

# 設定容器內工作目錄
WORKDIR /app

# 複製所有專案檔案進去
COPY . .

# 安裝套件
RUN pip install --no-cache-dir -r requirements.txt

# 啟動 Flask app，用 gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8080", "main:app"]

