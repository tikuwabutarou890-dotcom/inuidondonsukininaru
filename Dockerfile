FROM python:3.11-slim

WORKDIR /app

ENV PATH="/root/.local/bin:${PATH}"

ARG CACHEBUST=1

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --user gunicorn

COPY flasker ./flasker
COPY fly.toml .
COPY README.md .

CMD ["/root/.local/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "flasker:create_app"]
