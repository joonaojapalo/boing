# CMJ Evaluation Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure CMJ heights on the downloaded test videos with the parabola method and judge whether its error is small enough to continue.

**Architecture:** Python + MediaPipe extracts pose landmarks per frame (exact timestamps) into JSON. A pure TypeScript analysis module (reusable later in the web app) finds jumps, fits parabolas and computes heights plus quality checks. A TS evaluation script runs the analysis over all videos and writes a report; a Python script plots each jump for visual inspection.

**Tech Stack:** Python 3.9 venv (mediapipe 1.1, opencv, numpy, matplotlib), Node 26 + TypeScript + Vitest + tsx.

**Spec:** `docs/superpowers/specs/2026-10-13-cmj-web-prototype-design.md`

## Global Constraints

- Test videos, models and derived data live in `../boing-data/` and are never committed.
- `src/analysis/` has no DOM or Node dependencies (it must run in the browser later).
- Jump height = COM rise after takeoff; primary `h = g/2·(t_apex − t_off)²`, secondary `h = g·(t_on − t_off)²/8`, g = 9.81.
- No differentiation of keypoint positions; only curve fits.
- Deviation from spec: pose extraction for evaluation is Python, not Playwright; the web UI is deferred until the evaluation verdict.

---

### Task 1: Project scaffold + manifest

**Files:** `package.json`, `tsconfig.json`, `.gitignore`, `testdata/videos.json`

- [ ] npm project with typescript, vitest, tsx; `npm test` runs vitest.
- [ ] `.gitignore`: `node_modules`, `.venv`, `dist`.
- [ ] Manifest entries: `{id, file, source, view, arms: "hips"|"free"|"bar", notes, reference?: number[]}` for the 8 usable videos from the spec.
- [ ] Commit.

### Task 2: Pose extraction (Python)

**Files:** `tools/extract_pose.py`, `requirements.txt`

**Produces:** `../boing-data/landmarks/<id>.json`:
`{video, width, height, fps, frames: [{t, lm: [[x, y, z, visibility] × 33] | null}]}` (x, y normalised 0–1, t in seconds from the decoder timestamp).

- [ ] PoseLandmarker in VIDEO mode, heavy model, one pose.
- [ ] Skip videos whose output exists unless `--force`.
- [ ] Run on all manifest videos.
- [ ] Commit.

### Task 3: Quadratic fit (TS, TDD)

**Files:** `src/analysis/fit.ts`, `src/analysis/fit.test.ts`

**Produces:** `fitQuadratic(t: number[], y: number[]): {a, b, c, rms}` (y = a·t² + b·t + c, centred internally for conditioning), `quadraticRoots(q, level): [number, number] | null`.

- [ ] Tests: exact parabola recovered; noisy parabola within tolerance; roots at a level; no roots → null.
- [ ] Implement; tests green; commit.

### Task 4: Signals from landmarks (TS, TDD)

**Files:** `src/analysis/signals.ts`, `src/analysis/signals.test.ts`, `src/analysis/types.ts`

**Produces:** `toSignals(video: PoseVideo): Signals` with arrays `t`, `hip`, `toe`, `bodyPx` (height-up, pixels; NaN where landmarks missing or visibility < 0.5). hip = mean of landmarks 23/24, toe = mean of 31/32, bodyPx = nose (0) to mean heel (29/30) distance.

- [ ] Tests on hand-made landmark frames (y flipped to height-up, pixel scaling, missing frames → NaN).
- [ ] Implement; commit.

### Task 5: Jump detection + measurement (TS, TDD)

**Files:** `src/analysis/jumps.ts`, `src/analysis/jumps.test.ts`, `src/analysis/synthetic.ts` (test helper: CMJ model from the spike, any fps/noise/height, rendered as Signals)

**Produces:** `findJumps(s: Signals, opts?): Jump[]` where
`Jump = {tOff, tOn, tApex, hPrimary, hFlight, airborneFrames, gImplied, hipRmsRel, toeRmsRel, floorShiftRel, flags: string[]}`.

Algorithm:
1. Noise σ of toe = 1.4826·MAD of first differences / √2 over the whole series.
2. Airborne candidates: runs where toe − local floor > max(4σ, 2 % of median bodyPx); local floor = median toe over the 0.5 s window ending 0.1 s before the run. Keep runs lasting 0.15–1.2 s.
3. Floor after landing = median toe over 0.1–0.6 s after the run; `floorShiftRel` = |after − before| / bodyPx.
4. Fit toe and hip parabolas over the run's frames; `tOff`/`tOn` = toe roots at floor-before level; `tApex` = hip vertex.
5. Heights per the global formulas. `gImplied` = −2·a_hip / (bodyPx / (0.92·1.75 m)) (stature default 1.75 m, option).
6. Flags: `few-frames` (< 8), `g-implausible` (outside 6.5–13 m/s²), `poor-fit` (rms > 1.5 % bodyPx), `disagree` (|hPrimary − hFlight| > 15 % of hFlight), `camera-moved` (floorShiftRel > 2 %), `not-parabola` (hip a ≥ 0).

- [ ] Tests on synthetic jumps: 30 cm jump at 30/60/240 fps within 1 cm; two jumps found; quiet standing → none; a step/shuffle (one foot) → none or flagged; 2× slow-motion → `g-implausible`.
- [ ] Implement; commit.

### Task 6: Evaluation runner + plots

**Files:** `tools/evaluate.ts`, `tools/plot_jumps.py`

- [ ] `npm run evaluate`: for each manifest video with landmarks, run `findJumps`, write `../boing-data/results/results.json` and print a markdown table (video, arms, jump #, t, hPrimary, hFlight, frames, gImplied, flags, reference).
- [ ] `plot_jumps.py`: per jump a PNG of hip/toe height vs time with the fitted parabolas and events.
- [ ] Run, inspect plots, tune thresholds only with a stated reason; commit.

### Task 7: Verdict report

**Files:** `docs/evaluation/2026-10-13-first-evaluation.md`

- [ ] Summarise per video: detected vs actual jumps, heights, flags, repeatability within a person, comparison with reference values, failure modes, and a recommendation on whether the method is worth continuing and what accuracy to expect.
- [ ] Commit.
