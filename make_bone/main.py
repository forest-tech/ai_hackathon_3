"""
Flask app: upload an image -> detect human pose via MediaPipe -> draw bones (skeleton) on the image -> return processed image
Single-file app. No template files required (uses render_template_string).

Requirements:
  pip install flask mediapipe opencv-python-headless numpy pillow

Run:
  python image_with_bones_flask_app.py

Then open http://127.0.0.1:5000 in your browser.

Notes:
- MediaPipe does person pose estimation and provides landmark coordinates.
- If MediaPipe doesn't detect a person, the original image is returned with a small message overlay.
- This implementation draws the pose connections defined by MediaPipe, but you can customize colors/thickness etc.
"""

from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import cv2
from flask import Flask, request, send_file, render_template_string

import mediapipe as mp

app = Flask(__name__)

mp_pose = mp.solutions.pose
POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

INDEX_HTML = """
<!doctype html>
<title>Image → Bones (Pose) Overlay</title>
<h1>Upload an image to add bones (skeleton)</h1>
<form method=post enctype=multipart/form-data action="/process">
  <input type=file name=file accept="image/*">
  <input type=submit value="Upload & Process">
</form>
<p>Notes: Uses MediaPipe Pose to detect human keypoints and draws bones.
"""


def draw_pose_on_image_cv2(image_bgr: np.ndarray) -> np.ndarray:
    """Detect pose with MediaPipe and draw lines between landmarks on the image (BGR).
    Returns the image with the skeleton overlay.
    """
    h, w = image_bgr.shape[:2]
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(image_rgb)

    # If nothing detected, return original image with a small text overlay
    if not results.pose_landmarks:
        pil = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        draw.text((10, 10), "No pose detected", fill=(255, 0, 0), font=font)
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    # Draw landmarks and connections
    landmark_points = []
    for lm in results.pose_landmarks.landmark:
        # Convert normalized coords to pixel coords
        landmark_points.append((int(lm.x * w), int(lm.y * h), lm.visibility if hasattr(lm, 'visibility') else 1.0))

    # Draw connections (bones)
    overlay = image_bgr.copy()
    for connection in POSE_CONNECTIONS:
        start_idx, end_idx = connection
        if start_idx < len(landmark_points) and end_idx < len(landmark_points):
            x1, y1, v1 = landmark_points[start_idx]
            x2, y2, v2 = landmark_points[end_idx]
            # Only draw if both points have reasonable visibility
            if v1 > 0.2 and v2 > 0.2:
                cv2.line(overlay, (x1, y1), (x2, y2), (0, 255, 0), thickness=max(2, int(round(h/200))))

    # Draw joints as circles
    for (x, y, v) in landmark_points:
        if v > 0.2:
            cv2.circle(overlay, (x, y), radius=max(2, int(round(h/200))), color=(0, 0, 255), thickness=-1)

    # Blend overlay for nicer look
    output = cv2.addWeighted(overlay, 0.9, image_bgr, 0.1, 0)
    return output


@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return 'No file part', 400
    f = request.files['file']
    if f.filename == '':
        return 'No selected file', 400

    img_stream = f.read()

    # Read image into OpenCV
    img_np = np.frombuffer(img_stream, np.uint8)
    img_bgr = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return 'Cannot decode image', 400

    processed = draw_pose_on_image_cv2(img_bgr)

    # Encode processed image to PNG and return
    is_success, buffer = cv2.imencode('.png', processed)
    if not is_success:
        return 'Failed to encode image', 500

    io_buf = BytesIO(buffer.tobytes())
    io_buf.seek(0)
    return send_file(io_buf, mimetype='image/png', as_attachment=False, download_name='with_bones.png')


if __name__ == '__main__':
    # For local development only. Use a production WSGI server for deployment.
    app.run(debug=True)
