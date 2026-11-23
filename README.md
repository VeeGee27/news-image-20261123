# news-image-20261123 — The World Today

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/VeeGee27/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/VeeGee27/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One image summing up Monday 23 November 2026 in world news: 39 stories
across 5 regions on a single newspaper front page.

- 3 heroes: NATO meets as Poland confirms Russian missiles; Taiwan bans
  short selling as the Asia rout deepens; India's record 720 denied as the
  Wellington Test ends in a draw.
- 13 illustrated mid cards, each with a CONFIRMED / REPORTED source tag.
- 23 briefs, a numbered world map with every story pinned at its true
  location, a DATE CHECK box listing near-miss stories from other days,
  a stat strip and a region bar.
- Warm newsprint paper, serif masthead and headlines. Every story is
  dated Monday 23 November 2026 (events that happened, or were first
  reported, on that day).

## Build

`draw.py` (PIL) renders `entry.png` (1024×1024, deterministic) at build
time. `main.py` (standard library only) copies the pre-rendered image to
`$MAKEFUN_OUTPUT_DIR`, byte-verified.

```sh
python3 draw.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see LICENSE.
