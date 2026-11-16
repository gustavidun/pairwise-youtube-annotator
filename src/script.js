console.log("[script.js] Script initialized");

const accessCode = sessionStorage.getItem("access_code");
const sessionId = sessionStorage.getItem("session_id");

console.log("[script.js] accessCode:", accessCode, "sessionId:", sessionId);

if (!accessCode || !sessionId) {
    console.warn("[script.js] Missing credentials, redirecting to index.html...");
    window.location.replace("index.html");
}

let progress = -1;
const total = 100;
let currentPair = null;

function updateProgress() {
    const progressLabel = document.querySelector(".progress-snippet");
    const progressBar = document.querySelector(".progress-bar div");
    progress++;
    console.log("[script.js] Progress:", progress);
    if (progressBar) progressBar.style.width = `${Math.min((progress / total) * 100, 100)}%`;
    if (progressLabel) progressLabel.textContent = `${progress} / ${total}`;
}

function formatTags(rawTags) {
    if (!rawTags || rawTags === "[]") return "";
    const cleaned = rawTags.replace(/[\[\]']/g, "").trim();
    return cleaned ? `Tags: ${cleaned}` : "";
}

async function loadPair() {
    console.log("[script.js] loadPair() starting...");
    try {
        const response = await fetch("/fetch_pair");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        currentPair = data;
        console.log("[script.js] Received pair data:", data);

        const heading = document.querySelector("h1");
        if (heading) heading.textContent = data.question;

        const iframes = document.querySelectorAll("iframe");
        if (iframes.length >= 2) {
            iframes[0].src = `https://www.youtube.com/embed/${data.video_a}`;
            iframes[1].src = `https://www.youtube.com/embed/${data.video_b}`;
        }

        // Populate Video A metadata
        const titleA = document.getElementById("video-a-title");
        const descA = document.getElementById("video-a-description");
        const tagsA = document.getElementById("video-a-tags");
        if (titleA) titleA.textContent = data.video_a_title || "";
        if (descA) descA.textContent = data.video_a_description || "";
        if (tagsA) tagsA.textContent = formatTags(data.video_a_tags);

        // Populate Video B metadata
        const titleB = document.getElementById("video-b-title");
        const descB = document.getElementById("video-b-description");
        const tagsB = document.getElementById("video-b-tags");
        if (titleB) titleB.textContent = data.video_b_title || "";
        if (descB) descB.textContent = data.video_b_description || "";
        if (tagsB) tagsB.textContent = formatTags(data.video_b_tags);

        updateProgress();
    } catch (error) {
        console.error("[script.js] Failed to load pair:", error);
    }
}

async function chooseVideo(choice) {
    if (!accessCode) {
        alert("Access code required. Redirecting to start page.");
        window.location.replace("index.html");
        return;
    }

    if (currentPair) {
        try {
            const winner = choice === "A" ? currentPair.video_a : currentPair.video_b;
            await fetch("/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    code: accessCode,
                    video_a: currentPair.video_a,
                    video_b: currentPair.video_b,
                    winner: winner,
                    question: currentPair.question,
                    session_id: sessionId
                }),
            });
        } catch (error) {
            console.error("[script.js] Failed to submit annotation:", error);
        }
    }

    await loadPair();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadPair);
} else {
    loadPair();
}
