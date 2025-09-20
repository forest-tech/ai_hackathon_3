from flask import Flask, render_template, request, send_from_directory
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_video():
    file = request.files.get("video")
    if not file:
        return "No file uploaded", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    processed_path = os.path.join(PROCESSED_FOLDER, "half_" + file.filename)

    # ffmpeg コマンドで再生速度を2倍にして動画時間を半分にする
    # -filter:v "setpts=0.5*PTS" → 動画を2倍速に
    cmd = [
        "ffmpeg", "-y",
        "-i", filepath,
        "-filter:v", "setpts=0.5*PTS",
        "-an",  # 音声なし（必要に応じて削除可）
        processed_path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return f"ffmpeg error: {e.stderr.decode()}", 500

    return {"processed_video": "/processed/" + "half_" + file.filename}

@app.route("/processed/<filename>")
def serve_processed(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
