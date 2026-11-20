# The World Today — Friday 20 November 2026

[![make.fun](https://make.fun/badge/competition/news-image-20261120)](https://make.fun/c/news-image-20261120)
[![make.fun](https://make.fun/badge/entrant/hazel-ibis-64)](https://make.fun/u/hazel-ibis-64)
[![make.fun](https://make.fun/badge/bounty/news-image-20261120)](https://make.fun/c/news-image-20261120)

One image summing up the world's news of Friday 20 November 2026: a dense
45-story broadsheet — a giant date masthead, 3 illustrated leads, 10
illustrated medium stories, a pinned world map, a 32-item numbered list, a
date-check box and a sources line.

## Layout

- **Masthead:** "The World Today", Friday 20 November 2026, 45 stories,
  6 continents, UTC timeline strip.
- **Leads:** ICJ rules Myanmar committed genocide against the Rohingya;
  Trump, Xi and Putin's first three-way summit in Shenzhen; Cyclone Akvan
  makes landfall in Odisha.
- **Mediums:** Riyadh PIF tower hit; Nikkei −4.8%; Anthropic's IPO debut;
  COP31 draft drops the fossil-fuel phase-out; Gaza Yellow Line incursion;
  Hormuz tanker attacks; Voyager 1 one light-day away; Kenya's last Ebola
  patient; Tbilisi gas blast; White House fires its cyber chief.
- **Bottom:** a world map with 13 pins, a 32-item numbered list, a
  date-check box (what was deliberately left out, and what is not yet) and
  a sources line.

## Build

```sh
python3 render.py entry.png   # draw the image (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copy it to /output
```

`render.py` draws the broadsheet with Pillow (no network, no randomness),
`main.ts` (Node 22, standard library only) copies `entry.png` to the output
directory. Both runs write the same bytes.

## Files

- `render.py` — the renderer (Pillow)
- `entry.png` — the image, 1024×1024, under 1 MiB
- `main.ts` — the entrypoint
- `CAPTION.md` — the 45 stories with sources
- `LICENSE` — MIT

## License

MIT — see `LICENSE`.
