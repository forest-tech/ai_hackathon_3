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
anim = g.get("animations",[{}])[0]
scores = {}  # node_idx -> (name, dur, net, total)

for ch in anim.get("channels",[]):
    if ch["target"].get("path") != "translation": continue
    node = ch["target"]["node"]; name = g["nodes"][node].get("name","")
    s = anim["samplers"][ch["sampler"]]
    t = acc_np(g, bin_path, s["input"])
    v = acc_np(g, bin_path, s["output"])  # (N,3)
    dur = float(t[-1]-t[0]) if len(t)>1 else 0.0
    total = float(np.sum(np.linalg.norm(np.diff(v,axis=0),axis=1))) if len(v)>1 else 0.0
    net = float(np.linalg.norm(v[-1]-v[0])) if len(v)>1 else 0.0
    best = scores.get(node, (name,0,0,0))
    # 同一ノードに複数チャネルが来た場合は最大のtotalを採用
    if total > best[3]: scores[node]=(name,dur,net,total)

top = sorted(scores.values(), key=lambda x: x[3], reverse=True)[:10]
print("Top movers (by translation total):")
for name,dur,net,total in top:
    print(f"- {name:>20s} | dur={dur:.2f}s net={net:.3f} total={total:.3f}")
if not top:
    print("No translation keys found; motion may be rotation-only.")

