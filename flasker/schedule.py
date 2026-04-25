from flask import Blueprint, request, jsonify, session
from .database import get_db

bp = Blueprint("schedule", __name__)

# ▼ スケジュール一覧（全員OK）
@bp.route("/api/schedule/list")
def api_list_schedule():
    conn = get_db()
    rows = conn.execute("SELECT * FROM schedules ORDER BY date, time").fetchall()
    conn.close()

    result = {}
    for r in rows:
        date = r["date"]
        if date not in result:
            result[date] = []
        result[date].append({
            "id": r["id"],
            "time": r["time"],
            "url": r["url"],
            "title": r["title"],
            "thumbnail": r["thumbnail"]
        })

    return jsonify(result)


# ▼ スケジュール追加（管理者だけOK）
@bp.route("/api/schedule/add", methods=["POST"])
def api_add_schedule():

    # ★ 管理者チェック（追加）
    if not session.get("admin"):
        return jsonify({"error": "not_admin"}), 403

    data = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO schedules (date, time, url, title, thumbnail) VALUES (?, ?, ?, ?, ?)",
        (data["date"], data["time"], data["url"], data.get("title"), data.get("thumbnail"))
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


# ▼ スケジュール削除（管理者だけOK）
@bp.route("/api/schedule/delete", methods=["POST"])
def api_delete_schedule():

    # ★ 管理者チェック（既にOK）
    if not session.get("admin"):
        return jsonify({"error": "not_admin"}), 403

    data = request.json
    conn = get_db()
    conn.execute("DELETE FROM schedules WHERE id = ?", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})
