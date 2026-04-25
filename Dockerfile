FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# flasker ディレクトリをコピー
COPY flasker ./flasker

# 他の必要ファイルだけコピー（. を丸ごとコピーしない）
COPY fly.toml .
COPY .env .
COPY Dockerfile .
COPY README.md .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "flasker:app", "--access-logfile", "-"]
