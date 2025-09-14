import bpy, sys, os

argv = sys.argv
argv = argv[argv.index("--") + 1 :]  # -- 以降
model_path, motion_path, output_path = argv

ext = os.path.splitext(model_path)[1].lower()
if ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=model_path)
elif ext == ".obj":
    bpy.ops.wm.obj_import(filepath=model_path)  # ★ Blender 4.0以降はこちら
elif ext in [".glb", ".gltf"]:
    bpy.ops.import_scene.gltf(filepath=model_path)
else:
    raise ValueError(f"Unsupported model format: {ext}")

# 1. 不要な白い箱を削除
for obj in bpy.data.objects:
    if obj.type == "MESH" and "Cube" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. カメラを後方に移動して引く
camera = bpy.data.objects.get("Camera")
if camera:
    camera.location = (0, -6, 1.5)  # Zを1.5にして少し見下ろす
    camera.rotation_euler = (1.2, 0, 0)  # 見下ろし角度
    # 焦点距離を少し広角に
    camera.data.lens = 35

# 3. アニメーションが有効か確認
for obj in bpy.data.objects:
    if obj.animation_data and obj.animation_data.action:
        print(f"アニメーション確認: {obj.name} に {obj.animation_data.action.name}")

# 4. MP4で書き出し
bpy.context.scene.render.image_settings.file_format = "FFMPEG"
bpy.context.scene.render.ffmpeg.format = "MPEG4"
bpy.context.scene.render.ffmpeg.codec = "H264"
bpy.context.scene.render.filepath = output_path

bpy.ops.render.render(animation=True)
