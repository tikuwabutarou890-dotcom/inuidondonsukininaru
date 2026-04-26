# ▼ schedule.py
from flask import Blueprint, request, jsonify, session
from .database import get_db

bp = Blueprint("schedule", __name__)

# ▼ スケジュール追加（管理者だけOK）
@bp.route("/api/schedule/add", methods=["POST"])
def api_add_schedule():

    if not session.get("admin"):
        return jsonify({"error": "not_admin"}), 403

    data = request.json
    date = data["date"]
    time = data["time"]
    url = data["url"]

    # ★ 30分刻みチェック
    hh, mm = time.split(":")
    if mm not in ["00", "30"]:
        return jsonify({"error": "invalid_time"}), 400

    # ▼ /live/xxxx → watch?v=xxxx に変換
    fixed_url = url
    if "/live/" in url:
        try:
            video_id = url.split("/live/")[1].split("?")[0]
            fixed_url = f"https://www.youtube.com/watch?v={video_id}"
        except:
            pass

    # ▼ タイトル取得（サーバー側なら CORS なし）
    title = None
    try:
        import requests
        oembed = f"https://www.youtube.com/oembed?url={fixed_url}&format=json"
        data_oembed = requests.get(oembed).json()
        title = data_oembed.get("title")
    except:
        title = None

    # ▼ サムネイル生成
    thumbnail = None
    try:
        video_id = fixed_url.split("v=")[1]
        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    except:
        pass

    # ▼ DB 保存
    conn = get_db()
    conn.execute(
        "INSERT INTO schedules (date, time, url, title, thumbnail) VALUES (?, ?, ?, ?, ?)",
        (date, time, url, title, thumbnail)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# ▼ スケジュール削除（管理者だけOK）
@bp.route("/api/schedule/delete", methods=["POST"])
def api_delete_schedule():

    if not session.get("admin"):
        return jsonify({"error": "not_admin"}), 403

    data = request.json
    conn = get_db()
    conn.execute("DELETE FROM schedules WHERE id = ?", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})
