# Native app (React Native, Android) against the web pipeline

Date: 2026-10-14. Branch `react-native`. The app's video import (`mobile/`, native decoder + MediaPipe
Pose Landmarker in `modules/react-native-boing-pose`) against the web pipeline's results
(`../boing-data/results/results.json`: heavy model, every frame) on the user's own recordings.
Run with `mobile/scripts/analyze-on-device.sh` (the app downloads the video from this computer
over `adb reverse` and logs its result).

The app reads files in two passes when they run faster than ~35 fps (real time): the full model at
~30 fps over the whole file to find jumps, then the heavy model on every frame from 1.2 s before
takeoff to 1.0 s after landing. 30 fps files get one pass with the heavy model.

## Results (accepted jumps; takeoff→apex / flight-time height, app − web)

| Video | fps | Device | Jumps web / app | Δ takeoff→apex | Δ flight-time |
|---|---|---|---|---|---|
| `VID-20261013-WA0000` (WhatsApp) | 30 | emulator, Tab A8 | 1 / 1 | 0.0 | +0.1 |
| `20261013_173409` (variable rate, ≤ 60) | 35 avg | Tab A8 | 5 / 5 | −0.4 … +0.3 | +0.1 … +1.1 |
| `20261013_174604` | 60 | emulator, Tab A8 | 2 / 2 | −0.5 … +0.6 | −0.3 … +0.1 |
| `20261013_174441` | 120 | emulator, Tab A8 | 2 / 2 | −0.8 … +0.3 | −0.3 … +0.1 |

Takeoff times agree within 10 ms; frames in the air agree exactly. The remaining differences come
from the decoders (browser vs. Android MediaCodec, and the app's subsampled YUV→RGB conversion)
and, for two-pass files, from the windowed analysis (MediaPipe's VIDEO-mode tracking starts fresh
in each window).

## Bugs found and fixed on the way

- **Variable-frame-rate recordings taken for slow motion.** Samsung's normal recordings write
  `com.android.capture.fps = 60` but average 35 fps. Judging slow motion from the average fps
  squeezed every jump (heights ≈ 5 cm). Now judged from the shortest frame gaps (`peakFps`),
  for the whole file, as the web app does, also inside the second pass.
- **Budget hardware decoders reject some phone videos** (Galaxy Tab A8: the 1080p 60 fps HEVC
  file). The app now tries every decoder for the format, hardware first, then software.
- **GPU inference can fail after the model loads** (emulator); the landmarker now falls back to
  the CPU at the first failed inference.

## Speed

Galaxy Tab A8 (Unisoc T618, GPU delegate): 24 s of 30 fps video in 2 min 53 s with the heavy model
(≈ 0.24 s per frame); 8 s of 60 fps video in 4 min 27 s (software decoding, heavy model on both
passes, before the first pass switched to the full model). Fast phones should be several times
quicker; not measured yet.

## Emulator notes (Apple M4 Mac)

- Android 15 images advertise SME/SVE2 to the guest; MediaPipe's CPU path (XNNPACK) then dies with
  SIGILL. Use an Android 13 image (`system-images;android-33;google_apis;arm64-v8a`).
- GPU inference only works with `-gpu host`; SwiftShader fails (`GL_INVALID_ENUM`).
- Apps can't read files pushed with `adb` (scoped storage), hence the download over `adb reverse`.
