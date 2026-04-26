# ▼ schedule.py
from flask import Blueprint, request, jsonify, session
from .database import get_db

# ▼ Blueprint（必ず url_prefix を付ける）
bp = Blueprint("schedule", __name__, url_prefix="/schedule")

# ▼ スケジュール一覧（カード表示に必須）
@bp.route("/list")
def api_list_schedule():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, date, time, url, title, thumbnail FROM schedules ORDER BY date, time"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ▼ スケジュール追加（管理者だけOK）
@bp.route("/add", methods=["POST"])
def api_add_schedule():

    if not session.get("admin"):
        return jsonify({"error": "not_admin"}), 403

    data = request.json

    # ▼ 必須項目
    date = data.get("date")
    time = data.get("time")
    url = data.get("url")

    if not date or not time or not url:
        return jsonify({"error": "missing_fields"}), 400

    # ▼ 秒付き "12:00:00" → "12:00" に変換
    parts = time.split(":")
    if len(parts) >= 2:
        hh = parts[0]
        mm = parts[1]
        time = f"{hh}:{mm}"
    else:
        return jsonify({"error": "invalid_time"}), 400

    # ★ 30分刻みチェック
    if mm not in ["00", "30"]:
        return jsonify({"error": "invalid_time"}), 400

    # ▼ script.js から送られてくる title / thumbnail をそのまま使う
    title = data.get("title") or ""
    thumbnail = data.get("thumbnail") or ""

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
@bp.route("/delete", methods=["POST"])
def api_delete_schedule():

    if not session.get("admin"):
        return jsonify({"error": "not_admin"}), 403

    data = request.json
    schedule_id = data.get("id")

    if not schedule_id:
        return jsonify({"error": "missing_id"}), 400

    conn = get_db()
    conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})
