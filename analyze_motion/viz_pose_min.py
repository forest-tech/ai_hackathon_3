import sys, cv2, mediapipe as mp

inp = sys.argv[1]
out = sys.argv[2]
cap = cv2.VideoCapture(inp)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(out, fourcc, fps, (w, h))

pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1)
draw = mp.solutions.drawing_utils
styles = mp.solutions.drawing_styles

while True:
    ok, frame = cap.read()
    if not ok: break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = pose.process(rgb)
    if res.pose_landmarks:
        draw.draw_landmarks(
            frame, res.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS,
            landmark_drawing_spec=styles.get_default_pose_landmarks_style()
        )
    out.write(frame)

cap.release(); out.release()
print("saved: overlay.mp4")

