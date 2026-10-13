# Slow-motion reference session (240 fps, hand-marked)

Date: 2026-10-14. Video `own-20261014_020914` (Samsung Galaxy S24+, back camera, slow motion: 240 fps
captured, 29.96 fps playback). Phone on the floor tilted up, socks on tiles, hands on hips, 7 CMJs.

## Truth

Takeoff (last foot off) and landing (first foot down) marked frame by frame on foot crops (4.2 ms per
frame; ±1–2 frames). Flight times 342–397 ms, i.e. **14.4–19.4 cm** flight-time height (mean ≈ 17).
Stored as the manifest reference. The highest point from the top of the head was only reliable on some
jumps (the head nods; the detector failed in some light), so takeoff→apex has no independent truth here.

Pitfall found on the way: the extractor's time scale (playback fps from the fastest frame gaps ÷ capture
fps = 0.12504) and "frame index ÷ 240" (0.12485) differ by 0.16 %. Irrelevant within a jump (< 1 ms), but
it adds up to 72 ms by 46 s, so absolute times must be compared on one clock.

## Boing (heavy, VIDEO mode) against it

| | mean | sd |
|---|---|---|
| takeoff | 30 ms early | 18 ms |
| landing | 27 ms late | 6 ms |
| highest point vs flight midpoint | +2 ms | 16 ms |
| flight-time height | **+4.7 cm** | 0.8 cm |
| takeoff→apex height (vs flight-time truth) | **+3.7 cm** | 1.3 cm |

(Without the jump at 31.2 s, which Boing flags poor-fit: 40.8 / 26.8 cm for a 16.1 cm jump.)

The same widening appears in IMAGE mode and with real-time timestamps (no smoothing involved), and with a
local edge estimate instead of the toe parabola. Cause: the toe landmark (MediaPipe "foot index") sits around
the ball of the foot. In a tiptoe takeoff the heel rises and that point leaves the floor before the toe tips;
in a tiptoe landing the toe tips touch first and the point reaches the floor only as the heel comes down.
In IMAGE mode one foot's landmark sat ≈ 35 px (≈ 5 cm) above the real toe while the foot was pointed.

Tried, not good enough: lower of the two feet (+5.1 cm), extending the toe point along heel→toe (α 0.75:
+3.0 cm, sd 2.7, but −6.7 cm on the athlete video), local edges (no better).

On the athlete video (30 fps, WhatsApp) Boing's flight time matched the pixels within 0.4 cm, so the bias
depends on the person/footwear/camera (how high the heels are at takeoff and landing, socks vs shoes).
Open question: does the +4–5 cm also apply to the 30 fps live sessions (24–25 cm)?
