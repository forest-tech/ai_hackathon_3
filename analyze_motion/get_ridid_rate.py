import csv
det=tot=0
with open("poses.csv") as f:
    r=csv.reader(f); header=next(r)
    for row in r:
        tot+=1
        det+= (row[1]!="")  # 1番目のキー点xが空でなければ検出あり
print(f"frames={tot}, detected={det}, rate={det/max(tot,1):.1%}")
