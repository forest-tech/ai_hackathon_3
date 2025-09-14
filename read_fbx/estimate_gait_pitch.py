import json, sys, numpy as np

CT={5126:np.float32}; TS={"SCALAR":1,"VEC3":3}
def acc_np(g, bin_path, i):
    a=g["accessors"][i]; bv=g["bufferViews"][a["bufferView"]]
    off=bv.get("byteOffset",0)+a.get("byteOffset",0); n=TS[a["type"]]; cnt=a["count"]
    with open(bin_path,"rb") as f: f.seek(off); raw=f.read(bv["byteLength"])
    arr=np.frombuffer(raw, dtype=CT[a["componentType"]], count=cnt*n)
    return arr.reshape(cnt,n) if n>1 else arr

gltf_path, bin_path = sys.argv[1], sys.argv[2]
g = json.load(open(gltf_path, "r", encoding="utf-8"))
anim = g["animations"][0]

# Hips の translation チャンネルを取得
hips_idx = next(i for i,n in enumerate(g["nodes"]) if n.get("name","") in {"Hips","mixamorig:Hips"})
ch = next(ch for ch in anim["channels"] if ch["target"].get("path")=="translation" and ch["target"]["node"]==hips_idx)
s = anim["samplers"][ch["sampler"]]
t = acc_np(g, bin_path, s["input"]).astype(np.float64)  # (N,)
v = acc_np(g, bin_path, s["output"]).astype(np.float64) # (N,3)

dur = float(t[-1]-t[0]); net = float(np.linalg.norm(v[-1]-v[0]))
speed = net/dur if dur>0 else 0.0

# 前進軸を自動推定：総変位が最大の平面軸
disp = v[-1]-v[0]
fwd_axis = np.argmax(np.abs(disp[[0,2]]))  # 0:x or 2:z
h = v[:, [0,2]][:, fwd_axis]               # 前進方向の位置列
h = h - np.linspace(h[0], h[-1], len(h))   # 純移動を除去して周期成分を抽出

# FFTで 0.5〜4 Hz のピーク（歩行〜小走り帯域）
dt = np.mean(np.diff(t)); fs = 1.0/dt if dt>0 else 0.0
freqs = np.fft.rfftfreq(len(h), d=dt); H = np.abs(np.fft.rfft(h))
band = (freqs>=0.5) & (freqs<=4.0)
peak_f = float(freqs[band][np.argmax(H[band])]) if band.any() else 0.0

print(f"dur={dur:.2f}s speed={speed:.3f} m/s peak_freq≈{peak_f:.2f} Hz")

