# backend.py
from flask import Flask, send_file, request
import io
import numpy as np
import scipy.io.wavfile as wav

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("front.html")

@app.route("/generate", methods=["GET"])
def generate():
    # クエリパラメータから周波数を取得 (デフォルト440Hz)
    freq = float(request.args.get("freq", 440))

    # 音声生成パラメータ
    rate = 44100  # サンプリングレート
    duration = 2  # 秒

    t = np.linspace(0, duration, int(rate*duration), False)
    data = 0.5 * np.sin(2 * np.pi * freq * t)

    # 16bit PCM 形式に変換
    pcm = np.int16(data * 32767)

    buf = io.BytesIO()
    wav.write(buf, rate, pcm)
    buf.seek(0)

    return send_file(
        buf,
        mimetype="audio/wav",
        as_attachment=True,
        download_name="tone.wav"
    )

if __name__ == "__main__":
    app.run(debug=True)
