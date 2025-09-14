import bpy, sys, os

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # -- 以降
model_path, motion_path, output_path = argv

ext = os.path.splitext(model_path)[1].lower()
if ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=model_path)
elif ext == ".obj":
    bpy.ops.wm.obj_import(filepath=model_path)   # ★ Blender 4.0以降はこちら
elif ext in [".glb", ".gltf"]:
    bpy.ops.import_scene.gltf(filepath=model_path)
else:
    raise ValueError(f"Unsupported model format: {ext}")

# モーションはFBX想定
bpy.ops.import_scene.fbx(filepath=motion_path)

# 出力設定
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.image_settings.file_format = "FFMPEG"
bpy.ops.render.render(animation=True)
