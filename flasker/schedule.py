import datetime

def get_week_schedule():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday())  # 月曜開始

    week = []
    for i in range(7):
        day = start + datetime.timedelta(days=i)
        week.append({
            "date": day.strftime("%m/%d (%a)"),
            "items": []   # ← ここに予定を入れる
        })

    return week