import json, sys, numpy as np

CT={5126:np.float32}; TS={"SCALAR":1,"VEC3":3}
def acc_np(g, bin_path, i):
    a=g["accessors"][i]; bv=g["bufferViews"][a["bufferView"]]
    off=bv.get("byteOffset",0)+a.get("byteOffset",0); n=TS[a["type"]]; cnt=a["count"]
    with open(bin_path,"rb") as f: f.seek(off); raw=f.read(bv["byteLength"])
    arr=np.frombuffer(raw, dtype=CT[a["componentType"]], count=cnt*n)
    return arr.reshape(cnt,n) if n>1 else arr

gltf_path, bin_path = sys.argv[1], sys.argv[2]
g = json.load(open(gltf_path,"r",encoding="utf-8"))
anim = g["animations"][0]
# Hips translation
hips_idx = next(i for i,n in enumerate(g["nodes"]) if n.get("name","") in {"Hips","mixamorig:Hips"})
ch = next(ch for ch in anim["channels"] if ch["target"].get("path")=="translation" and ch["target"]["node"]==hips_idx)
s = anim["samplers"][ch["sampler"]]
t = acc_np(g, bin_path, s["input"]).astype(np.float64)   # (N,)
v = acc_np(g, bin_path, s["output"]).astype(np.float64)  # (N,3)

dur = float(t[-1]-t[0]) if len(t)>1 else 0.0
net = float(np.linalg.norm(v[-1]-v[0])) if len(v)>1 else 0.0
speed = net/dur if dur>0 else 0.0

# 前進軸（x or z）を自動選択し、純移動を引いて周期だけ取り出す
disp = v[-1]-v[0]
fwd_axis = int(np.argmax(np.abs(disp[[0,2]])))  # 0:x or 2:z（インデックスは後で 0→x, 1→z に写像）
fwd_comp = v[:,0] if fwd_axis==0 else v[:,2]
trend = np.linspace(fwd_comp[0], fwd_comp[-1], len(fwd_comp))
osc = fwd_comp - trend

# 簡易ピーク検出（移動平均で平滑→局所極大）
def moving_avg(x, k=5):
    k = max(1, k); w = np.ones(k)/k
    return np.convolve(x, w, mode="same")
y = moving_avg(osc, k=max(3, len(osc)//100))
dy = np.diff(y); sign = np.sign(dy); cross = np.where(np.diff(sign) < 0)[0]  # 山の頂点
# 極端なノイズ除去（振幅しきい値）
thr = 0.02 * (np.max(y)-np.min(y) + 1e-6)
peaks = [i for i in cross if y[i] - np.min(y[max(0,i-10):i+11]) > thr]

# “山”1つを「片足接地の1山」と見なして **歩数 ≈ ピーク数**（粗い近似）
steps = len(peaks)
# ストライド（2歩で1サイクル） ≈ 歩数/2
stride_count = max(1, steps//2)
stride_len = net / stride_count if stride_count>0 else 0.0

# 上下振幅（Y成分のpeak-to-peak）
vert_amp = float(np.max(v[:,1]) - np.min(v[:,1])) if len(v)>0 else 0.0

print(f"dur={dur:.2f}s speed={speed:.3f} m/s steps≈{steps} stride_len≈{stride_len:.3f} m vert_amp≈{vert_amp:.3f} m")

