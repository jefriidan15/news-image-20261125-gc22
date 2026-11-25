[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/jefriidan15/news-image-20261125-gc22/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/jefriidan15/news-image-20261125-gc22/reward.svg)](https://make.fun/bounty/news-image-20261125)

# The World in One Image — 25 November 2026

A program that draws one newspaper front page summing up Wednesday
25 November 2026's world news, for the
[news-image-20261125](https://make.fun/bounty/news-image-20261125) bounty.

## The day in one image

- **Lead:** Ukraine sinks a Russian warship off Libya; Zelenskiy confirms
  the Gulf of Finland strike as Norway urges caution.
- **NATO sends AWACS to Poland** after missiles land on NATO soil.
- **Houthis hit Riyadh's PIF Tower, 11 hurt** — the second strike in
  under a week.
- **Huawei convicted** in a US criminal trial over its Iran business.
- **Trump awards Rudy Giuliani the Medal of Freedom.**
- **700,000 Russian troops killed**, a new analysis finds.
- Also today: GTA 6 out since Nov 19, England level the T20 series,
  South Korea's education minister quits in an exam scandal, the UN court
  finds Myanmar guilty over the Rohingya, Waymo pulls driverless taxis off
  US freeways, and the CIA and ODNI are hit by a breach.

## How it works

`main.py` is pure Python standard library (`zlib` + `struct` only). It
draws the front page on a 1024x1024 canvas with a built-in 5x7 bitmap
font and writes a PNG with no timestamps, so two runs produce
byte-identical output.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, under 1 MiB) and prints its
size and sha256 after a read-back check.

## License

MIT — see [LICENSE](LICENSE).
