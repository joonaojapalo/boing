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
- MediaPipe's temporal smoothing (VIDEO mode) is not the main cause. Re-running in
  IMAGE mode (every frame independent, `extract_pose.py --mode image`) gave
  52.5 / 48.4 / 51.5 cm against the mat's 52.9 / 52.8 / 54.6 cm (mean error −2.6 vs
  −3.0 cm, within noise), with noisier fits. VIDEO mode stays the default.

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

The extractor already supports decimation (`--every 2|4|8`, evaluated with
`npm run evaluate -- --variant @every4`). Still to verify: that OpenCV reads the real
240 fps timestamps of iPhone slow-motion `.mov` files (rather than the 30 fps playback rate).

## Addendum: own recordings (Android, phone on the floor tilted up)

Three videos, no reference device. All 9 jumps were detected and pass the checks.

| Video | Capture | Jumps: h_P / h_F (cm) | g implied |
|---|---|---|---|
| 20261013_173409 | 30 fps, variable rate (60 fps stretches) | 20.6 / 22.8, 22.8 / 24.4, 22.6 / 26.0, **22.0 / 22.2 (60 fps)**, 29.3 / 26.7 | 6.2–8.5 |
| 20261013_174441 | **120 fps slow motion**, stored at 29.6 fps | 23.3 / 24.3, 22.7 / 22.4 (≈50 frames in flight each) | 6.0–6.9 |
| 20261013_174604 | 4K, 60 fps | 27.4 / 26.9, 26.3 / 23.9 | 7.7–8.1 |

Findings:

- **The height measurement is angle-robust**: it uses only event times (toe-off, toe
  touchdown, hip apex), which a tilted or side-on camera doesn't change. Results are
  consistent across 30/60/120 fps: 22–27 cm, and at 60–120 fps the two methods agree
  within ≈1–2 cm per jump.
- **The implied-g check is not angle-robust**: its body-size scale is distorted by a
  floor-level camera tilted up (g read 6–8.5 on every jump). The bounds were widened
  from 6.5–13 to 4–20 m/s². That still rejects ≥ 2× slow motion (g ≤ 2.5) and caught a
  wrong time base in practice (see below).
- **Slow motion**: Samsung writes `com.android.capture.fps` (e.g. 120) and stores the
  file at a 30 fps playback rate. The extractor now reads it (`tools/mp4meta.py`) and
  stores `timeScale` with the landmarks. Variable-frame-rate recordings *also* report a
  high capture fps (their maximum, 60), so a file only counts as slow motion if its
  shortest frame gaps are clearly longer than 1/capture fps. The first, naive rule
  misread the variable-rate video as slowed; the g check flagged it (g ≈ 19–26).
- Samsung also writes `SlowMotion_Data` (`21488:36888:3` here). Its meaning is unknown;
  the whole clip turned out to be uniformly slowed (both jumps give the same g).

## Addendum: lighter pose models and toe creep (2026-10-14)

A phone session (Android 10, live switched to the **lite** model) gave refined heights of
22–52 cm for jumps the athlete judged all ≈ 26 cm; the high ones were flagged poor-fit.
Cause: with lite (and sometimes full), the toe point **creeps up slowly** (≈ 5 % of body
height over 0.2–0.3 s) while the heels rise in the push-off, and stays raised after landing.
The airborne run then started at the creep, the flight looked longer, and the fits included
non-free-fall frames. Heavy rarely does this.

Fix (`trimCreep` in `src/analysis/jumps.ts`): flight starts where the toes' fast rise begins
and ends where the fast fall stops (speed measured over ≥ 50 ms, "fast" ≥ 25 % of the jump's
fastest); the edges are at that contact level. Only trimmed when the creep is small and short
(≤ 10 % of body height, ≤ 0.4 s), so jumps without creep give exactly the previous results.

Effect (takeoff→apex, cm; `@lite`/`@full` landmarks via `extract_pose.py --model …`):

- Own 30 fps recording, full model: an outlier of 95 → 21; lite: 41.7 → 23.1; full at 15 fps: 64.7 → 22.3.
- The phone session's live frames (≈ 21 fps): 42, 61, 20, 31, 46, 26, 47 → 26, 24, 20, 31, 26, 26, 38.
- All reference videos (contact mat, force plate) and heavy-model results: unchanged.
- Flight frames are now counted honestly, so at ≈ 15 fps some jumps fall below the 8-frame
  minimum ("too short"); live, those are measured again from the 30 fps recording.

Lite also misses more jumps than full (3 of 5 vs 5 of 5 on the 30 fps recording), so with
continuous recording on, the app no longer switches to lite on slow phones.

## Addendum: athlete video with a My Jump reference (2026-10-14)

`own-VID-20261013-WA0000` (front, phone on the floor tilted up, WhatsApp copy 480x848 at 30 fps,
one CMJ). My Jump: **22.25 cm** (flight time). Boing: flight time 23.6 cm (heavy), 24.9 (full),
23.9 (lite); takeoff→apex 20.9 / 23.2 / 22.1. The app's file mode gave 21.4 cm (as reported).
Flight time reads ≈ 1.4 cm above My Jump with heavy, about one frame of flight at 30 fps.
