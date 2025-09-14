#!/bin/bash

# ファイルパス
MODEL_PATH="data/model/white_man.obj"
MOTION_PATH="data/motion/HipHop.fbx"
OUTPUT_PATH="video_creator/output/sample" # outputは強制的にmkvになる

# Blender実行
blender -b --python video_creator/apply_motion_v2.py -- "$MODEL_PATH" "$MOTION_PATH" "$OUTPUT_PATH"

# mkv ファイルをmp4に変換する
# ffmpeg -i "$OUTPUT_PATH" -c copy output.mp4


# 旧コード
# blender -b --python apply_motion.py -- data/model/white_man.fbx data/motion/sample_motion.fbx video_creator/output/sample.mp4
