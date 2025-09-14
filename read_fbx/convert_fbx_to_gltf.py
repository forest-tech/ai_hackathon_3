import bpy, sys

# 引数: -- <input.fbx> <output.gltf>
argv = sys.argv[sys.argv.index("--")+1:]
fbx_path, gltf_path = argv

# クリーンな状態で開始
bpy.ops.wm.read_factory_settings(use_empty=True)

# FBX 読み込み（必要に応じてオプション調整）
bpy.ops.import_scene.fbx(filepath=fbx_path, automatic_bone_orientation=True)

# glTF 書き出し（4.5は 'GLB' か 'GLTF_SEPARATE' のみ）
bpy.ops.export_scene.gltf(
    filepath=gltf_path,
    export_format='GLTF_SEPARATE',  # .gltf(JSON) + .bin + テクスチャ
    # 余計な指定は外して互換優先（必要なら後から追加）
)

