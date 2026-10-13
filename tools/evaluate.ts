/**
 * Run the jump analysis on every manifest video that has extracted landmarks.
 * Usage: npm run evaluate -- [--data ../boing-data] [--min-visibility 0.5] [--variant @image]
 * Writes <data>/results/results.json and prints a markdown table.
 */
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { findJumps } from "../src/analysis/jumps";
import { toSignals } from "../src/analysis/signals";
import type { PoseVideo } from "../src/analysis/types";

const repo = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const opt = (name: string, def: string) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : def;
};
const data = resolve(opt("--data", join(repo, "..", "boing-data")));
const minVisibility = Number(opt("--min-visibility", "0.5"));
// Landmark variant from extract_pose.py, e.g. "@image" or "@every4".
const variant = opt("--variant", "");

interface Entry { id: string; arms: string; view: string }
const manifest: Entry[] = JSON.parse(readFileSync(join(repo, "testdata", "videos.json"), "utf8"));

const results = [];
console.log("| video | arms | # | t_off s | h primary cm | h flight cm | frames | g implied | flags |");
console.log("|---|---|---|---|---|---|---|---|---|");
for (const e of manifest) {
  const path = join(data, "landmarks", `${e.id}${variant}.json`);
  if (!existsSync(path)) continue;
  const video: PoseVideo = JSON.parse(readFileSync(path, "utf8"));
  const signals = toSignals(video, { minVisibility });
  const jumps = findJumps(signals);
  results.push({ id: e.id, arms: e.arms, fps: video.fps, signals, jumps });
  if (jumps.length === 0) console.log(`| ${e.id} | ${e.arms} | – | | | | | | no jumps |`);
  jumps.forEach((j, k) =>
    console.log(
      `| ${e.id} | ${e.arms} | ${k + 1} | ${j.tOff.toFixed(2)} | ${(j.hPrimary * 100).toFixed(1)} | ` +
        `${(j.hFlight * 100).toFixed(1)} | ${j.airborneFrames} | ${j.gImplied.toFixed(1)} | ${j.flags.join(", ")} |`,
    ),
  );
}
mkdirSync(join(data, "results"), { recursive: true });
writeFileSync(join(data, "results", `results${variant}.json`), JSON.stringify(results));
