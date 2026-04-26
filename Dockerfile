FROM python:3.11-slim

WORKDIR /app

# pip install --user のインストール先を PATH に追加
ENV PATH="/root/.local/bin:${PATH}"

ARG CACHEBUST=1

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --user gunicorn

# flasker フォルダをコピー
COPY flasker ./flasker

COPY fly.toml .
COPY README.md .

# create_app() を使うのでこれが正解
CMD ["/root/.local/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "flasker:create_app()"]

