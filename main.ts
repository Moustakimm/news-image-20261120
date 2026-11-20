// The World Today — Friday 20 November 2026.
//
// This is the entrypoint for the 20 November 2026 news-image entry. The
// broadsheet itself is rendered by render.py (Python + Pillow) and shipped
// beside this file as entry.png — a dense 45-story front page with three
// illustrated leads, ten illustrated mediums, a pinned world map, a
// 32-item numbered list, a date-check box and a sources line.
//
// This program does exactly one thing: it copies those exact entry.png
// bytes into the grader's output directory, so both graded runs produce
// an identical file. No network, no dependencies, Node 22 standard
// library only.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = join(here, "entry.png");
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
writeFileSync(target, readFileSync(source));
