import json, sys, numpy as np

CT = {5126: np.float32}; TS = {"SCALAR":1,"VEC3":3,"VEC4":4}
def acc_np(g, bin_path, i):
    a=g["accessors"][i]; bv=g["bufferViews"][a["bufferView"]]
    off=bv.get("byteOffset",0)+a.get("byteOffset",0); n=TS[a["type"]]; cnt=a["count"]
    with open(bin_path,"rb") as f: f.seek(off); raw=f.read(bv["byteLength"])
    arr=np.frombuffer(raw, dtype=CT[a["componentType"]], count=cnt*n)
    return arr.reshape(cnt,n) if n>1 else arr

gltf_path, bin_path = sys.argv[1], sys.argv[2]
g = json.load(open(gltf_path,"r",encoding="utf-8"))
anims = g.get("animations", [])
print(f"animations: {len(anims)}")
if not anims: sys.exit(0)

# ルート候補（よくある名前）
root_names = {"Hips","Root","root","Master","Armature","mixamorig:Hips"}
for ai,anim in enumerate(anims):
    # translationチャンネルを探す
    cand=[]
    for ch in anim["channels"]:
        if ch["target"].get("path")!="translation": continue
        node_idx = ch["target"]["node"]
        name = g["nodes"][node_idx].get("name","")
        if name in root_names or node_idx==0: cand.append((node_idx, ch["sampler"], name))
    if not cand: print(f"[{ai}] no translation channel"); continue
    node_idx,samp,name = cand[0]
    samp=anim["samplers"][samp]
    t = acc_np(g, bin_path, samp["input"])
    v = acc_np(g, bin_path, samp["output"])  # (N,3)
    dist_total = float(np.sum(np.linalg.norm(np.diff(v,axis=0),axis=1))) if len(v)>1 else 0.0
    net = float(np.linalg.norm(v[-1]-v[0])) if len(v)>1 else 0.0
    dur = float(t[-1]-t[0]) if len(t)>1 else 0.0
    label = "locomotion" if net>0.2 else "in-place/idle-ish"
    print(f"[{ai}] name='{anim.get('name','')}' root='{name}' dur={dur:.2f}s net={net:.3f} total={dist_total:.3f} -> {label}")

