progress = -1
total = 50

function updateProgress() {
    const progressLabel = document.querySelector(".progress-snippet");
    const progressBar = document.querySelector(".progress-bar div");
    progress++;
    console.log(progress);
    progressBar.style.width = `${(progress / total) * 100}%`;
    progressLabel.textContent = `${progress} / ${total}`;
}

async function loadPair() {
    try {
        const response = await fetch("/fetch_pair");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

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

window.onload = loadPair;
