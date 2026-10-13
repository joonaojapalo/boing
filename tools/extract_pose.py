"""Extract MediaPipe pose landmarks for every frame of the manifest videos.

Usage: .venv/bin/python -I tools/extract_pose.py [--data ../boing-data] [--force] [ids...]
Writes <data>/landmarks/<id>.json (see docs/superpowers/plans/2026-10-13-cmj-evaluation.md).
"""
import argparse
import json
import os
import sys

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract(video_path, model_path, mode="video", every=1):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {video_path}")
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        # VIDEO mode tracks and smooths landmarks over time; IMAGE mode treats frames independently.
        running_mode=vision.RunningMode.VIDEO if mode == "video" else vision.RunningMode.IMAGE,
        num_poses=1,
    )
    frames = []
    last_ms = -1
    index = -1
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            index += 1
            if index % every:
                continue  # simulate a lower frame rate
            ms = max(int(round(t * 1000)), last_ms + 1)  # detector needs strictly increasing ms
            last_ms = ms
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
            result = landmarker.detect_for_video(image, ms) if mode == "video" else landmarker.detect(image)
            lm = None
            if result.pose_landmarks:
                lm = [[round(p.x, 5), round(p.y, 5), round(p.z, 5), round(p.visibility, 3)]
                      for p in result.pose_landmarks[0]]
            frames.append({"t": round(t, 6), "lm": lm})
    return {"video": os.path.basename(video_path), "width": width, "height": height, "fps": fps, "frames": frames}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(os.path.dirname(REPO), "boing-data"))
    ap.add_argument("--model", default="pose_landmarker_heavy.task")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--mode", choices=["video", "image"], default="video")
    ap.add_argument("--every", type=int, default=1, help="keep every Nth frame (simulates lower fps)")
    ap.add_argument("ids", nargs="*")
    args = ap.parse_args()

    with open(os.path.join(REPO, "testdata", "videos.json")) as f:
        manifest = json.load(f)
    out_dir = os.path.join(args.data, "landmarks")
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(args.data, "models", args.model)

    for entry in manifest:
        if args.ids and entry["id"] not in args.ids:
            continue
        suffix = ("" if args.mode == "video" else "@image") + ("" if args.every == 1 else f"@every{args.every}")
        out = os.path.join(out_dir, entry["id"] + suffix + ".json")
        if os.path.exists(out) and not args.force:
            print(f"skip {entry['id']} (exists)")
            continue
        print(f"extract {entry['id']} ...", flush=True)
        data = extract(os.path.join(args.data, entry["file"]), model_path, args.mode, args.every)
        data["id"] = entry["id"] + suffix
        data["fps"] = data["fps"] / args.every
        with open(out, "w") as f:
            json.dump(data, f, separators=(",", ":"))
        found = sum(1 for fr in data["frames"] if fr["lm"])
        print(f"  {len(data['frames'])} frames, pose in {found}, {data['fps']:.2f} fps", flush=True)


if __name__ == "__main__":
    sys.exit(main())
