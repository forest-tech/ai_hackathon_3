# save as extract_pose_min.py
import cv2, mediapipe as mp, csv, sys
vid = sys.argv[1]
cap = cv2.VideoCapture(vid)
pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1)
with open("poses.csv","w",newline="") as f:
    w = csv.writer(f); 
    # ヘッダ: frame, keypointごとに x,y,vis
    head = ["frame"] + [f"{n}_{c}" for n in range(33) for c in ("x","y","vis")]
    w.writerow(head)
    fno = 0
    while True:
        ok, frame = cap.read()
        if not ok: break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)
        row = [fno]
        if res.pose_landmarks:
            lm = res.pose_landmarks.landmark
            for i in range(33):
                row += [lm[i].x, lm[i].y, lm[i].visibility]
        else:
            row += ["" for _ in range(33*3)]
        w.writerow(row); fno += 1
cap.release()

