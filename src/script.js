const accessCode = sessionStorage.getItem("access_code");

// Guard: If no valid code was entered, redirect back to login immediately
if (!accessCode) {
    window.location.replace("index.html");
}

let progress = -1;
const total = 50;
let currentPair = null;

function updateProgress() {
    const progressLabel = document.querySelector(".progress-snippet");
    const progressBar = document.querySelector(".progress-bar div");
    progress++;
    console.log(progress);
    if (progressBar) progressBar.style.width = `${(progress / total) * 100}%`;
    if (progressLabel) progressLabel.textContent = `${progress} / ${total}`;
}

async function loadPair() {
    try {
        const response = await fetch("/fetch_pair");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        currentPair = data;

        const heading = document.querySelector("h1");
        if (heading) heading.textContent = data.question;

        const iframes = document.querySelectorAll("iframe");
        if (iframes.length >= 2) {
            iframes[0].src = `https://www.youtube.com/embed/${data.video_a}`;
            iframes[1].src = `https://www.youtube.com/embed/${data.video_b}`;
        }
        updateProgress();
    } catch (error) {
        console.error("Failed to load pair:", error);
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
                }),
            });
        } catch (error) {
            console.error("Failed to submit annotation:", error);
        }
    }

    await loadPair();
}

window.onload = loadPair;
