"""Plot every detected jump: hip and toe height vs time, with fitted parabolas and events.

Usage: .venv/bin/python -I tools/plot_jumps.py [--data ../boing-data] [ids...]
Reads <data>/results/results.json (from `npm run evaluate`), writes <data>/results/plots/<id>.png.
"""
import argparse
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def quad(q, t):
    x = np.asarray(t) - q["t0"]
    return q["a"] * x * x + q["b"] * x + q["c"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(os.path.dirname(REPO), "boing-data"))
    ap.add_argument("ids", nargs="*")
    args = ap.parse_args()
    res_dir = os.path.join(args.data, "results")
    with open(os.path.join(res_dir, "results.json")) as f:
        results = json.load(f)
    os.makedirs(os.path.join(res_dir, "plots"), exist_ok=True)

    for r in results:
        if args.ids and r["id"] not in args.ids or not r["jumps"]:
            continue
        s = r["signals"]
        t = np.array(s["t"], float)
        hip = np.array([np.nan if v is None else v for v in s["hip"]], float)
        toe = np.array([np.nan if v is None else v for v in s["toe"]], float)
        jumps = r["jumps"]
        cols = min(4, len(jumps))
        rows = math.ceil(len(jumps) / cols)
        fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 3.2 * rows), squeeze=False)
        for k, (ax, j) in enumerate(zip(axes.flat, jumps)):
            d = j["debug"]
            scale = 100 / (d["bodyPx"] / (0.92 * 1.75))  # px -> cm (approximate)
            m = (t > j["tOff"] - 1.0) & (t < j["tOn"] + 0.6)
            floor, hip0 = d["floor"], np.nanmedian(hip[(t > j["tOff"] - 1.6) & (t < j["tOff"] - 1.0)])
            ax.plot(t[m], (hip[m] - hip0) * scale, ".", ms=3, color="tab:blue", label="hip")
            ax.plot(t[m], (toe[m] - floor) * scale, ".", ms=3, color="tab:orange", label="toe")
            tf = np.linspace(j["tOff"] - 0.05, j["tOn"] + 0.05, 100)
            ax.plot(tf, (quad(d["hipFit"], tf) - hip0) * scale, "-", lw=1, color="tab:blue")
            ax.plot(tf, (quad(d["toeFit"], tf) - floor) * scale, "-", lw=1, color="tab:orange")
            for x, c in ((j["tOff"], "green"), (j["tOn"], "red"), (j["tApex"], "gray")):
                ax.axvline(x, color=c, lw=0.7, ls="--")
            ax.axhline(0, color="k", lw=0.5)
            flags = ",".join(j["flags"]) or "ok"
            ax.set_title(f"#{k + 1} t={j['tOff']:.2f}  P {j['hPrimary']*100:.1f} F {j['hFlight']*100:.1f} cm\n"
                         f"g {j['gImplied']:.1f}  n={j['airborneFrames']}  {flags}", fontsize=8)
            ax.tick_params(labelsize=7)
        for ax in list(axes.flat)[len(jumps):]:
            ax.axis("off")
        axes.flat[0].legend(fontsize=7)
        fig.suptitle(f"{r['id']} ({r['arms']}, {r['fps']:.0f} fps)  heights in ~cm vs stance", fontsize=10)
        fig.tight_layout()
        out = os.path.join(res_dir, "plots", f"{r['id']}.png")
        fig.savefig(out, dpi=80)
        plt.close(fig)
        print(out)


if __name__ == "__main__":
    main()
