document.getElementById("uploadForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById("processedVideo").src = data.processed_video;
    } else {
        alert("アップロードに失敗しました");
    }
});
