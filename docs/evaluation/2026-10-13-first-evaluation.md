# First evaluation: CMJ height from video by parabola fitting

Date: 2026-10-13
Data: 13 YouTube videos and 1 Instagram reel (`testdata/videos.json`), all 24–60 fps,
analysed with MediaPipe Pose (heavy) + `src/analysis`. Reproduce with:

```
.venv/bin/python -I tools/extract_pose.py   # landmarks → ../boing-data/landmarks
npm run evaluate                            # table + ../boing-data/results/results.json
.venv/bin/python -I tools/plot_jumps.py     # plots → ../boing-data/results/plots
```

## Summary

- **The physics holds on real video.** During flight the hip keypoint follows a clean
  parabola. The implied gravity (curvature ÷ an independent body-size scale) is
  **9.92 ± 0.58 m/s²** over 20 clean jumps from 10 different videos (true 9.81).
- **Against a contact mat (the only exact reference found), at 30 fps / 720p, oblique view:**
  our flight-time height reads 1.1, 3.9 and 4.1 cm low (mat: 52.9, 52.8, 54.6 cm).
  The cause is frame timing: at takeoff the toes move 8–15 cm per frame, so each edge
  is only located to about ±10–15 ms.
- **Repeatability within one session** (same athlete, 3 jumps): takeoff→apex
  48.1 / 47.6 / 46.6 cm (range 1.5 cm), versus the mat's 52.9 / 52.8 / 54.6 cm (range 1.8 cm).
- **Force plate (Hawkin), 1 jump, 30 fps:** takeoff→apex 43.7 cm, flight time 46.2 cm,
  plate 46.1 cm. The plate's display is blurry; it could also read 41.0 cm.
- **Not yet answered:** accuracy at 60–240 fps. None of the referenced videos is
  above 30 fps. That needs our own recordings (see "Next step").

Verdict: **worth continuing.** The method is physically sound and robust on
uncontrolled internet video. At 30 fps the error is about ±2–4 cm, which is too coarse
for the ±2 cm target. Simulation and the error analysis both say this should shrink
roughly in proportion to the frame interval, so 120–240 fps should land well inside ±2 cm.
That still has to be confirmed with real recordings.

## Results per video (clean jumps)

h_P = takeoff→apex (`g/2·(t_apex − t_off)²`), h_F = flight time (`g·T²/8`), cm.

| Video | Setup | Jumps: h_P / h_F | g implied | Reference |
|---|---|---|---|---|
| x-1aKYUhd_k | front, 30 fps, hips | 37.3 / 39.9 | 9.9 | – |
| DZV_RlzfSIY | side, 30 fps, hips | 35.7 / 36.0, 27.1 / 29.2 | 10.0, 9.6 | – |
| 0NWWXm8jg6g | front, 25 fps, barbell | 15.3 / 17.0, 13.0 / 16.5 | 9.0, 10.7 | – |
| ElIb8VBrjLM | front, 30 fps, arm swing | 42.3 / 40.3, 43.8 / 41.9, 40.5 / 39.2 | 9.6–9.9 | – |
| 3u1uz8ghdk0 | oblique, 30 fps, hips | 48.1 / 51.8, 47.6 / 48.9, 46.6 / 50.5 | 8.9–10.1 | **mat 52.9, 52.8, 54.6** |
| 3u1uz8ghdk0 | same, arm swing | 55.1 / 55.2 (+2 flagged poor-fit) | 9.7 | – |
| O-aTakZ5gwk | front, 30 fps, hips | 43.7 / 46.2 | 10.5 | plate 46.1 (or 41.0) |
| A33w43rknf0 | side, 30 fps, hips | 43.5 / 45.5, 45.0 / 48.5 | 9.6, 10.9 | athlete's history 38–47, mean 43 |
| CJ_BGt3G0jI | front, 24 fps, hips | 47.2 / 39.6 (flag: disagree) | 9.6 | – |
| _19utncgGV0 | front, 30 fps, hips | 43.7 / 45.7 | 9.9 | – |
| UABkrMpNunc | oblique, 30 fps, hips | 19.0 / 24.2, 20.1 / 26.5, 24.1 / 30.3 (flag: disagree) | 10.1–11.1 | – |
| Instagram reel | front, handheld, 30 fps | 5 jumps found, 38–50 cm, all but 2 flagged camera-moved | 9.1–12.7 | overlay ≈25 (unit unknown; matches neither cm nor inches) |
| 09yR5a4u-6A, A7GeA3lBpg8 | side, several people, arm swing | no clean jumps (all flagged) | – | – |

## Observations

1. **Flight time > takeoff→apex**, by 1.7 cm on average. That's expected: people land
   with more bent ankles and knees than at takeoff, which lengthens the flight. Contact
   mats and My Jump measure flight time and so include this. Force plates measure
   takeoff velocity, which is what h_P approximates. The two references differ by
   definition, so we should report the one matching the reference users compare against.
2. **The quality checks work.** Edited and handheld video produces many false
   candidates: scene cuts, walking, zooms. The g check and the floor-shift check
   rejected all of them; none survived as a clean result. A 2× slow-motion clip
   would give g ≈ 2.5 and be rejected.
3. **Arm swing is not detected by the g check** (the arms are held still in flight, so
   the hip stays parabolic). If hands-on-hips must be enforced, it needs a separate
   check on the wrists relative to the hips.
4. **The `disagree` flag** (h_P and h_F differ by > 15 %) fires on athletes who land
   very deep (UABkrMpNunc). That's useful as a "land with straight legs" hint, not an error.
5. **Side and oblique views work** as well as front views, because only vertical motion is used.
6. **Instagram reel:** not usable as a reference. The camera tilts to follow the jumper,
   and the overlay numbers don't match the visible flight times in any unit.

## Error budget at 30 fps (from the data)

- Takeoff/landing timing: about ±10–15 ms per edge → about ±1.5–4 cm on a 50 cm jump
  (dh/h = 2·dT/T).
- Systematic: our flight time came out 7–25 ms shorter than the mat's. Likely causes:
  motion blur and the foot extending/flexing near the ground, plus whatever offset the
  mat itself has. With n = 3, offset and noise can't be separated.
- Keypoint jitter: small in comparison (fit residuals ≈ 1 % of body height).

## Next step: decisive test with our own recordings

One session gives the full accuracy curve:

1. iPhone (or Android) **slow-motion 240 fps**, phone on a tripod or leaning still,
   2–3 m in front, about hip height, whole body including the feet in frame, good light.
2. 10–15 CMJs, hands on hips, landing "like the takeoff" (straight legs, on the toes).
   Add 2–3 bad ones (deep landing, arm swing).
3. Reference: count frames from takeoff to landing by hand in the 240 fps video
   (±4 ms ≈ ±0.6 cm), or use My Jump 2 on the same video. A contact mat or force
   plate at a gym is even better if available.
4. Analyse the 240 fps video, and the same video decimated to 120/60/30 fps
   (keep every 2nd/4th/8th frame). That shows exactly how the error depends on frame rate.

Before that, the tooling needs: (a) correct handling of slow-motion files (iPhone
slow-mo `.mov` stores 240 fps timestamps; verify that OpenCV reads them), and
(b) a decimation option in the extractor.
