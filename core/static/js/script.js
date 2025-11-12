function translateText() {
    const text = document.getElementById("input-text").value;
    const lang = document.getElementById("language").value;

    fetch("/translate/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `text=${encodeURIComponent(text)}&lang=${lang}`
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output-text").innerText = data.translated_text;
    });
}

function speakText() {
    const text = document.getElementById("output-text").innerText;
    const lang = document.getElementById("language").value;

    const audio = new Audio(`/tts/?text=${encodeURIComponent(text)}&lang=${lang}`);
    audio.play();
}

function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken'))
        .split('=')[1];
}