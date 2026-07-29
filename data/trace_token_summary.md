# Trace Token Extraction Summary

Extracted from `/home/tca/reprobench/eval/repro_trace` — 369 runs.

Token formula: `total = input + output + reasoning + cache.read + cache.write`

## Per-Model Aggregate

| Model | Runs | Avg Input | Avg Output | Avg Total | Avg Cost ($) | Avg Time (s) |
|-------|-----:|----------:|-----------:|----------:|-------------:|-------------:|
| claude-sonnet-4-6 | 77 | 4,148,924 | 26,157 | 4,175,081 | 1.92 | 758 |
| deepseek-v4-flash | 80 | 2,281,775 | 17,493 | 2,299,268 | 0.00 | 706 |
| glm-5.2 | 70 | 4,865,632 | 42,544 | 4,908,176 | 1.62 | 1,509 |
| gpt-5.5 | 55 | 1,234,595 | 7,366 | 1,241,962 | 1.25 | 239 |
| mimo-v2.5 | 87 | 3,121,711 | 17,286 | 3,138,997 | 0.00 | 995 |
| Overall | 369 | 3,203,509 | 22,495 | 3,226,004 | 0.89 | 868 |

## Cache Token Breakdown

| Model | Avg Cache Read | Avg Cache Write | Avg Reasoning | Avg Assistant Msgs |
|-------|---------------:|----------------:|--------------:|-------------------:|
| claude-sonnet-4-6 | 4,067,335 | 81,528 | 0 | 59 |
| deepseek-v4-flash | 2,226,968 | 0 | 4,354 | 42 |
| glm-5.2 | 4,722,864 | 0 | 0 | 57 |
| gpt-5.5 | 1,150,529 | 0 | 1,631 | 26 |
| mimo-v2.5 | 3,047,311 | 0 | 2,500 | 52 |
| Overall | 3,117,447 | 17,013 | 1,776 | 48 |

## Grand Totals

- Total runs with trace: 369
- Total tokens: 1,190,395,599
- Total cost: $329.36
- Total elapsed time: 320,162s (88.9h)
