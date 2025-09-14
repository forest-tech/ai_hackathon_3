承知しました！
これまでの一連の流れ（FBX→glTF変換、要約、bin解析、モーションの確認）を `README.md` 向けにまとめました。

---

# README.md

## 📦 プロジェクト概要

このリポジトリは **FBX ファイル（3Dモデル＋アニメーション）を AI 解析に適した形式に変換し、モーションを数値的に要約する**ためのツール群です。

* **入力**: `.fbx`
* **変換**: Blender (CLI) を用いて `.gltf` (JSON) + `.bin` に変換
* **出力**: JSON構造と数値を Python で解析し、モーション特徴量（移動距離・歩数・ピッチなど）を抽出

---

## 📂 ディレクトリ構成（例）

```
ai_hackathon_3/
├── convert_fbx_to_gltf.py        # FBX → glTF(SEPARATE) 変換スクリプト
├── summarize_gltf_min.py         # glTF の要約 (ノード数/メッシュ数/アニメ数)
├── quick_check_root_motion.py    # ルートモーションの有無と移動量の確認
├── scan_translation_activity.py  # ノードごとの移動量ランキング
├── estimate_gait_pitch.py        # Hips の移動から歩行ピッチを推定
├── estimate_steps_stride.py      # Hips の移動から歩数・ストライドを概算
├── estimate_steps_by_feet.py     # 足ボーンの上下動から歩数を推定
└── out/
    ├── output.gltf               # Blenderで生成されたJSON
    ├── output.bin                # バイナリデータ
    └── textures/                 # 画像がある場合
```

---

## 🚀 手順

### 1. FBX → glTF(SEPARATE) 変換

Blender を **ヘッドレスモード**で起動し、FBXをglTFに変換します。

```bash
blender -b -P convert_fbx_to_gltf.py -- input.fbx ./out/output.gltf
```

生成物:

* `output.gltf` … JSON 構造
* `output.bin` … 頂点座標・アニメキー値
* `textures/` … マテリアル画像

---

### 2. glTF の要約確認

```bash
uv run summarize_gltf_min.py ./out/output.gltf
```

例:

```json
{
  "node_count": 120,
  "mesh_count": 1,
  "animation_count": 1,
  "mesh_verts": [1524]
}
```

---

### 3. ルートモーションの有無を確認

```bash
uv run quick_check_root_motion.py ./out/output.gltf ./out/output.bin
```

例:

```
[0] name='actor_0|Scene' root='Master' dur=4.91s net=0.000 total=0.000 -> in-place/idle-ish
```

---

### 4. どのノードが動いているか調べる

```bash
uv run scan_translation_activity.py ./out/output.gltf ./out/output.bin
```

例:

```
Top movers (by translation total):
-                 Hips | dur=4.91s net=1.939 total=2.256
```

👉 Hips に大きな移動 → 歩行系モーションの可能性大。

---

### 5. 歩行ピッチの推定

```bash
uv run estimate_gait_pitch.py ./out/output.gltf ./out/output.bin
```

例:

```
dur=4.91s speed=0.395 m/s peak_freq≈0.61 Hz
```

👉 ゆっくり歩行。

---

### 6. 歩数やストライド長を推定

#### Hipsベース（粗い）

```bash
uv run estimate_steps_stride.py ./out/output.gltf ./out/output.bin
```

#### 足ボーンベース（推奨）

```bash
uv run estimate_steps_by_feet.py ./out/output.gltf ./out/output.bin
```

例:

```
steps≈8 (L:4, R:4)  dur=4.91s  speed=0.395 m/s
```

---

## ✅ まとめ

* **FBXはそのままでは扱いづらい → BlenderでglTFへ変換**
* `.gltf` = 構造情報(JSON), `.bin` = 実データ
* Pythonで `.bin` を展開 → 移動距離・歩数・ピッチ等を抽出
* これにより AI 解析が可能な「数値的特徴量サマリ」を得られる

---

👉 このREADMEをベースに、今後「AIに投げるための要約JSON」をさらに設計していけます。

---

ご要望に合わせて、この README を「もっと短く要点だけ」か「実行例を充実させるか」調整できますが、どちらにしましょうか？

