from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flasker.youtube import fetch_latest_videos
import requests
import os

bp = Blueprint("main", __name__)





# ============================
#   アクセスカウンター
# ============================
COUNTER_FILE = "counter.txt"

def read_counter():
    if not os.path.exists(COUNTER_FILE):
        return 0
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def write_counter(value):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(value))


# ============================
#   index
# ============================
@bp.route("/")
def index():
    count = read_counter()
    count += 1
    write_counter(count)

    videos = fetch_latest_videos(10)
    return render_template(
        "index.html",
        videos=videos,
        count=count,
        debug=is_admin()   # ← 追加
    )



# ============================
#   YouTube タイトル取得 API
# ============================
@bp.route("/api/title")
def get_title():
    video_id = request.args.get("id")
    if not video_id:
        return jsonify({"title": None})

    url = f"https://www.youtube.com/watch?v={video_id}"
    api = f"https://noembed.com/embed?url={url}"

    try:
        res = requests.get(api, timeout=5)
        data = res.json()
        return jsonify({"title": data.get("title")})
    except:
        return jsonify({"title": None})


# ============================
#   ここ好きページ
# ============================
@bp.route("/kokosuki")
def kokosuki():
    return render_template("kokosuki.html", admin=session.get("admin"))


# ============================
#   コラボページ
# ============================
@bp.route("/collab")
def collab():
    is_admin = session.get("admin", False)
    return render_template("collab.html", IS_ADMIN=is_admin)



# ============================
#   ログイン (.env 対応)
# ============================
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        admin_password = os.getenv("ADMIN_PASSWORD")  # ← .env から読む

        if password == admin_password:
            session["admin"] = True
            return redirect("/")
        else:
            return "パスワードが違います"

    return render_template("login.html")



# ============================
#   ログアウト
# ============================
@bp.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("main.index"))

# ============================
#   デバックモード
# ============================
def is_admin():
    return session.get("admin") is True

# ============================
#   アクセス解析
# ============================
import logging
from flask import request

@app.before_request
def log_request_info():
    app.logger.info(f"{request.remote_addr} {request.method} {request.path}")
