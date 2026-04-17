// ===============================
// ▼ YouTube 情報取得
// ===============================
function extractYouTubeId(url) {
    try {
        const u = new URL(url);

        if (u.searchParams.get("v")) return u.searchParams.get("v");
        if (u.hostname === "youtu.be") return u.pathname.slice(1);
        if (u.pathname.startsWith("/shorts/")) return u.pathname.split("/")[2];
        if (u.pathname.startsWith("/live/")) return u.pathname.split("/")[2];

        return null;
    } catch {
        return null;
    }
}

// ▼ Flask API でタイトル取得
async function fetchYouTubeTitle(videoId) {
    try {
        const res = await fetch(`/api/title?id=${videoId}`);
        const data = await res.json();
        return data.title || "タイトル取得失敗";
    } catch {
        return "タイトル取得失敗";
    }
}


// ===============================
// ▼ weekList（月曜始まり）
// ===============================
let schedules = JSON.parse(localStorage.getItem("schedules") || "{}");

// ▼ 今が基準。-1 = 先週、1 = 来週
let weekOffset = 0;

function renderWeekList() {
    const weekList = document.getElementById("weekList");
    weekList.innerHTML = "";

    const today = new Date();

    // ▼ 今週の月曜日
    const monday = new Date(today);
    monday.setDate(today.getDate() - ((today.getDay() + 6) % 7));

    // ▼ 週オフセットを反映
    monday.setDate(monday.getDate() + weekOffset * 7);

    for (let i = 0; i < 7; i++) {
        const d = new Date(monday);
        d.setDate(monday.getDate() + i);

        const dateKey = d.toISOString().split("T")[0];

        const card = document.createElement("div");
        card.className = "day-card";
        card.innerHTML = `
            <h3>${d.getMonth() + 1}/${d.getDate()}</h3>
            <div id="day-${dateKey}" class="schedule-area"></div>
        `;

        weekList.appendChild(card);

        renderDaySchedules(dateKey);
    }
}


// ===============================
// ▼ 1日のスケジュール描画（管理者だけ削除ボタン）
// ===============================
function renderDaySchedules(dateKey) {
    const container = document.getElementById(`day-${dateKey}`);
    if (!container) return;

    container.innerHTML = "";

    if (!schedules[dateKey]) return;

    schedules[dateKey].forEach((item, index) => {
        const div = document.createElement("div");
        div.className = "schedule-card";

        const isYouTube = item.thumbnail !== null;

        // ▼ 管理者だけ削除ボタンを表示
        let deleteButtonHtml = "";
        if (IS_ADMIN) {
            deleteButtonHtml = `
                <button class="delete-btn" onclick="deleteSchedule('${dateKey}', ${index})">×</button>
            `;
        }

        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong class="schedule-time">${item.time}</strong>
                ${deleteButtonHtml}
            </div>

            ${
                isYouTube
                    ? `
                    <a href="${item.url}" target="_blank">
                        <img src="${item.thumbnail}" class="schedule-thumb">
                    </a>
                    `
                    : ""
            }

            <div style="margin-top:6px;">
                ${item.title ? `<div>${item.title}</div>` : ""}
                ${!isYouTube ? `<a href="${item.url}" target="_blank">${item.url}</a>` : ""}
            </div>
        `;

        container.appendChild(div);
    });
}


// ===============================
// ▼ スケジュール追加
// ===============================
async function addSchedule() {
    const date = document.getElementById("dateInput").value;
    const time = document.getElementById("timeInput").value;
    const url = document.getElementById("urlInput").value;

    if (!date || !time || !url) {
        alert("日付・時間・URLを入力してください");
        return;
    }

    const videoId = extractYouTubeId(url);
    let thumbnail = null;
    let title = null;

    if (videoId) {
        thumbnail = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
        title = await fetchYouTubeTitle(videoId);
    }

    if (!schedules[date]) schedules[date] = [];

    schedules[date].unshift({
        time,
        url,
        thumbnail,
        title
    });

    localStorage.setItem("schedules", JSON.stringify(schedules));

    renderDaySchedules(date);

    document.getElementById("urlInput").value = "";
}


// ===============================
// ▼ 初期表示 + 週送りボタン
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    renderWeekList();

    const weekLeft = document.querySelector(".week-left");
    const weekRight = document.querySelector(".week-right");

    // ▼ 先週へ
    weekLeft.addEventListener("click", () => {
        weekOffset -= 1;
        renderWeekList();
    });

    // ▼ 来週へ
    weekRight.addEventListener("click", () => {
        weekOffset += 1;
        renderWeekList();
    });
});


// ===============================
// ▼ スケジュール削除
// ===============================
function deleteSchedule(dateKey, index) {
    if (!schedules[dateKey]) return;

    schedules[dateKey].splice(index, 1);

    if (schedules[dateKey].length === 0) {
        delete schedules[dateKey];
    }

    localStorage.setItem("schedules", JSON.stringify(schedules));

    renderDaySchedules(dateKey);
}


// ===============================
// ▼ デバッグ
// ===============================
document.addEventListener("mousemove", (e) => {
    const debug = document.getElementById("mouse-debug");
    debug.textContent = `x: ${e.clientX}, y: ${e.clientY}, h: ${e.pageY}`;
});
