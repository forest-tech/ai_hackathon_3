import csv, sys, math, statistics as stats

# 角度（°）を B 点の内角として計算（A-B-C）
def knee_angle(ax, ay, bx, by, cx, cy):
    ux, uy = ax - bx, ay - by
    vx, vy = cx - bx, cy - by
    nu = math.hypot(ux, uy); nv = math.hypot(vx, vy)
    if nu == 0 or nv == 0: return None
    cosv = max(-1.0, min(1.0, (ux*vx + uy*vy) / (nu * nv)))
    return math.degrees(math.acos(cosv))

# CSV列名ユーティリティ（nはランドマーク番号）
def col(n, comp):  # comp in {"x","y","vis"}
    return f"{n}_{comp}"

in_csv = sys.argv[1]
out_csv = sys.argv[2] if len(sys.argv) > 2 else "knee_angles.csv"

LHIP, LKNEE, LANK = 23, 25, 27
RHIP, RKNEE, RANK = 24, 26, 28
VIS_THR = 0.5  # visibilityしきい値（必要なら調整）

rows_out = []
L_vals, R_vals = [], []

with open(in_csv, newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        fr = int(row["frame"])
        def read_pt(n):
            try:
                x, y, v = float(row[col(n,"x")]), float(row[col(n,"y")]), float(row[col(n,"vis")])
                return (x, y, v)
            except:
                return (None, None, 0.0)

        lhx, lhy, lhv = read_pt(LHIP)
        lkx, lky, lkv = read_pt(LKNEE)
        lax, lay, lav = read_pt(LANK)
        rhx, rhy, rhv = read_pt(RHIP)
        rkx, rky, rkv = read_pt(RKNEE)
        rax, ray, rav = read_pt(RANK)

        L = R = ""
        if min(lhv, lkv, lav) >= VIS_THR:
            ang = knee_angle(lhx, lhy, lkx, lky, lax, lay)
            if ang is not None:
                L = f"{ang:.2f}"; L_vals.append(ang)
        if min(rhv, rkv, rav) >= VIS_THR:
            ang = knee_angle(rhx, rhy, rkx, rky, rax, ray)
            if ang is not None:
                R = f"{ang:.2f}"; R_vals.append(ang)

        rows_out.append({"frame": fr, "left_knee_deg": L, "right_knee_deg": R})

with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["frame","left_knee_deg","right_knee_deg"])
    w.writeheader(); w.writerows(rows_out)

def summary(name, vals):
    if not vals: return f"{name}: (no data)"
    return (f"{name}: n={len(vals)}  mean={stats.fmean(vals):.1f}°  "
            f"min={min(vals):.1f}°  max={max(vals):.1f}°  "
            f"p10={stats.quantiles(vals, n=10)[0]:.1f}°  p90={stats.quantiles(vals, n=10)[-1]:.1f}°")

print(f"saved: {out_csv}")
print(summary("LEFT", L_vals))
print(summary("RIGHT", R_vals))

