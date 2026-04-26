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

// ===============================
// ▼ DBから読み込み
// ===============================
let schedules = {};

async function loadSchedules() {
    const res = await fetch("/api/schedule/list");
    schedules = await res.json();
}

// ===============================
// ▼ weekList（月曜始まり）
// ===============================
let weekOffset = 0;

function formatDateJST(date) {
    const y = date.getFullYear();
    const m = ("0" + (date.getMonth() + 1)).slice(-2);
    const d = ("0" + date.getDate()).slice(-2);
    return `${y}-${m}-${d}`;
}

function renderWeekList() {
    const weekList = document.getElementById("weekList");
    weekList.innerHTML = "";

    const today = new Date();

    const monday = new Date(today);
    monday.setDate(today.getDate() - ((today.getDay() + 6) % 7));
    monday.setDate(monday.getDate() + weekOffset * 7);

    for (let i = 0; i < 7; i++) {
        const d = new Date(monday);
        d.setDate(monday.getDate() + i);

        const dateKey = formatDateJST(d);

        const card = document.createElement("div");
        card.className = "day-card";
        card.dataset.date = dateKey;   // ← 日付クリック用

        card.innerHTML = `
            <h3>${d.getMonth() + 1}/${d.getDate()}</h3>
            <div id="day-${dateKey}" class="schedule-area"></div>
        `;

        weekList.appendChild(card);

        renderDaySchedules(dateKey);
    }
}

// ===============================
// ▼ 1日のスケジュール描画（タイトル必ず表示版）
// ===============================
function renderDaySchedules(dateKey) {
    const container = document.getElementById(`day-${dateKey}`);
    if (!container) return;

    container.innerHTML = "";

    if (!schedules[dateKey]) return;

    schedules[dateKey].forEach(item => {
        const wrapper = document.createElement("div");

        wrapper.innerHTML = `
        <div class="schedule-card">

            <!-- ▼ 左側（リンク部分） -->
            <a href="${item.url}" target="_blank" class="schedule-main">
                <div class="schedule-time">${item.time}</div>

                ${
                    item.thumbnail
                        ? `<img src="${item.thumbnail}" class="schedule-thumb">`
                        : ""
                }

                <!-- ▼ タイトルを必ず表示 -->
                <div class="schedule-title" title="${item.title || ""}">
                    ${item.title || ""}
                </div>
            </a>

            <!-- ▼ 右側（削除ボタン） -->
            ${
                IS_ADMIN
                    ? `<button class="side-delete" data-id="${item.id}">×</button>`
                    : ""
            }

        </div>
        `;

        container.appendChild(wrapper);

        // ▼ 削除ボタン（リンクに吸われない）
        if (IS_ADMIN) {
            const btn = wrapper.querySelector(".side-delete");
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                deleteSchedule(item.id);
            });
        }
    });
}

// ===============================
// ▼ スケジュール追加
// ===============================
async function addSchedule() {
    if (!IS_ADMIN) {
        alert("スケジュールの追加は管理者のみです");
        return;
    }

    const date = document.getElementById("dateInput").value;
    const time = document.getElementById("timeInput").value;
    const url = document.getElementById("urlInput").value.trim();

    if (!date || !time || !url) {
        alert("日付・時間・URL を入力してください");
        return;
    }

    let videoId = extractYouTubeId(url);
    let thumbnail = null;
    let title = null;

    // ▼ /live/xxxx → watch?v=xxxx に変換
    let fixedUrl = url;
    if (url.includes("/live/")) {
        const id = extractYouTubeId(url);
        if (id) fixedUrl = `https://www.youtube.com/watch?v=${id}`;
    }

    try {
        // ▼ YouTube公式 oEmbed API（ライブでもタイトル取れる）
        const res = await fetch(`https://www.youtube.com/oembed?url=${fixedUrl}&format=json`);
        const data = await res.json();

        if (data.title) title = data.title;
    } catch (e) {
        console.log("oEmbed error:", e);
    }

    if (videoId) {
        thumbnail = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
    }

    const payload = { date, time, url, title, thumbnail };

    const res = await fetch("/api/schedule/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const result = await res.json();

    if (result.status === "ok") {
        await loadSchedules();
        renderWeekList();
    } else {
        alert("追加に失敗しました（管理者のみ）");
    }
}


// ===============================
// ▼ 削除
// ===============================
async function deleteSchedule(id) {
    const res = await fetch("/api/schedule/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
    });

    if (res.status === 403) {
        alert("管理者だけ削除できます");
        return;
    }

    await loadSchedules();
    renderWeekList();
}

// ===============================
// ▼ 日付クリック → 入力欄に反映
// ===============================
document.addEventListener("click", (e) => {
    const card = e.target.closest(".day-card");
    if (!card) return;

    const date = card.dataset.date;
    const input = document.getElementById("dateInput");
    if (input) input.value = date;

    // ハイライト
    document.querySelectorAll(".day-card").forEach(c => c.classList.remove("selected"));
    card.classList.add("selected");
});

// ===============================
// ▼ 初期表示
// ===============================
document.addEventListener("DOMContentLoaded", async () => {
    await loadSchedules();
    renderWeekList();

    document.querySelector(".week-left").addEventListener("click", async () => {
        weekOffset -= 1;
        await loadSchedules();
        renderWeekList();
    });

    document.querySelector(".week-right").addEventListener("click", async () => {
        weekOffset += 1;
        await loadSchedules();
        renderWeekList();
    });
});

// ===== マウスカーソル位置デバッグ =====
document.addEventListener("mousemove", (e) => {
    const box = document.getElementById("mouse-debug");
    if (!box) return;

    const x = e.clientX;
    const y = e.clientY;
    const h = window.scrollY + e.clientY;

    box.textContent = `x:${x} y:${y} h:${h}`;
});
