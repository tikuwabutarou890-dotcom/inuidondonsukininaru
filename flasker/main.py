from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from flasker.youtube import fetch_latest_videos
from flasker.database import get_db, get_count, increment_count
import requests
import os
import logging
import feedparser

bp = Blueprint("main", __name__)

# ============================
#   index（アクセスカウンター永続化）
# ============================
@bp.route("/")
def index():
    increment_count()
    count = get_count()

    videos = fetch_latest_videos(10)
    return render_template(
        "index.html",
        videos=videos,
        count=count,
        debug=is_admin()
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
#   ここ好き API（追加）
# ============================
@bp.route("/api/kokosuki/add", methods=["POST"])
def add_kokosuki():
    data = request.json
    url = data.get("url")
    title = data.get("title")
    comment = data.get("comment")
    minute = data.get("minute")
    second = data.get("second")
    thumbnail = data.get("thumbnail")

    conn = get_db()
    conn.execute("""
        INSERT INTO kokosuki (url, title, comment, minute, second, thumbnail)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (url, title, comment, minute, second, thumbnail))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ============================
#   ここ好き API（一覧）
# ============================
@bp.route("/api/kokosuki/list")
def list_kokosuki():
    conn = get_db()
    rows = conn.execute("SELECT * FROM kokosuki ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ============================
#   ここ好き API（削除）
# ============================
@bp.route("/api/kokosuki/delete", methods=["POST"])
def delete_kokosuki():
    if not session.get("admin"):
        return jsonify({"error": "not admin"}), 403

    data = request.json
    item_id = data.get("id")

    conn = get_db()
    conn.execute("DELETE FROM kokosuki WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ============================
#   コラボページ
# ============================
@bp.route("/collab")
def collab():
    is_admin = session.get("admin", False)
    return render_template("collab.html", IS_ADMIN=is_admin)

# ============================
#   コラボ API（追加）
# ============================
@bp.route("/api/collab/add", methods=["POST"])
def add_collab():
    data = request.json
    url = data.get("url")
    title = data.get("title")
    author = data.get("author")
    thumbnail = data.get("thumbnail")

    conn = get_db()

    # 重複削除
    conn.execute("DELETE FROM collab WHERE url = ?", (url,))

    conn.execute("""
        INSERT INTO collab (url, title, author, thumbnail)
        VALUES (?, ?, ?, ?)
    """, (url, title, author, thumbnail))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ============================
#   コラボ API（一覧）
# ============================
@bp.route("/api/collab/list")
def list_collab():
    conn = get_db()
    rows = conn.execute("SELECT * FROM collab ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ============================
#   コラボ API（削除）
# ============================
@bp.route("/api/collab/delete", methods=["POST"])
def delete_collab():
    if not session.get("admin"):
        return jsonify({"error": "not admin"}), 403

    data = request.json
    collab_id = data.get("id")

    conn = get_db()
    conn.execute("DELETE FROM collab WHERE id = ?", (collab_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ============================
#   ログイン (.env 対応)
# ============================
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        admin_password = os.getenv("ADMIN_PASSWORD")

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
#   デバッグモード
# ============================
def is_admin():
    return session.get("admin") is True

# ============================
#   アクセス解析ログ
# ============================
@bp.before_app_request
def log_request_info():
    current_app.logger.info(f"{request.remote_addr} {request.method} {request.path}")
    # ============================
#   YouTube 最新動画（RSS）
# ============================


@bp.route("/api/youtube/latest")
def youtube_latest():
    FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCXRlIK3Cw_TJIQC5kSJJQMg"

    feed = feedparser.parse(FEED_URL)

    videos = []
    for entry in feed.entries[:10]:
        video_id = entry.yt_videoid
        title = entry.title
        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        videos.append({
            "videoId": video_id,
            "title": title,
            "thumbnail": thumbnail
        })

    return jsonify(videos)

