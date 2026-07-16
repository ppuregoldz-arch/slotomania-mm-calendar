# Historical Prediction Backtest

**Generated:** 2026-07-10
**Design:** rolling-origin; every test day uses only prior data; test window 2026-04-01–2026-07-05.

## Overall results

| KPI | Test days | MAE | MAPE | Bias | Direction accuracy | 80%-residual range coverage |
|---|---:|---:|---:|---:|---:|---:|
| Revenue | 92 | $50,044 | 8.0% | $+13,498 | 41.6% | 72.8% |
| Paying users | 92 | 2,003 | 7.6% | +1,478 | 24.4% | 65.2% |
| Wager | — | — | — | — | insufficient evidence | insufficient evidence |
| Gem usage | — | — | — | — | insufficient evidence | insufficient evidence |

## Method

- Same-weekday mean is fitted from prior non-holiday days.
- Family effects are prior same-weekday residual means shrunk by `n/(n+10)`.
- Concurrent family effects are summed and capped at ±$100K revenue / ±5,000 PU.
- Expected range is prediction ± the prior 80th percentile absolute residual.
- This tests family/day association, not causal attribution.

## Family-level out-of-sample direction

| Family key | Revenue n | Revenue direction | PU n | PU direction |
|---|---:|---:|---:|---:|
| buyAll | 21 | 47.6% | 21 | 4.8% |
| coinSale | 8 | 62.5% | 8 | 25.0% |
| counterPo | 10 | 10.0% | 10 | 20.0% |
| customPod | 10 | 70.0% | 10 | 40.0% |
| decoyBonanza | 17 | 58.8% | 17 | 52.9% |
| extremeStamp | 16 | 56.2% | 16 | 25.0% |
| fortuneDip | 6 | 0.0% | 6 | 16.7% |
| gemback | 28 | 7.1% | 28 | 10.7% |
| goldenSpin | 11 | 54.5% | 11 | 45.5% |
| happyHour | 28 | 3.6% | 28 | 3.6% |
| mgapBigger | 11 | 9.1% | 11 | 18.2% |
| mgapBogo | 16 | 56.2% | 16 | 18.8% |
| mgapMatched | 6 | 16.7% | 6 | 0.0% |
| mgapOther | 16 | 31.2% | 16 | 12.5% |
| mgapWildSymbols | 4 | 50.0% | 4 | 0.0% |
| priceCut | 14 | 50.0% | 14 | 28.6% |
| prizeMania | 10 | 20.0% | 10 | 20.0% |
| rolling | 38 | 52.6% | 38 | 10.5% |
| rollingMoreForLess | 13 | 69.2% | 13 | 15.4% |
| ryd | 44 | 4.5% | 44 | 4.5% |
| snl | 15 | 0.0% | 15 | 6.7% |

## Failure cases and limits

- Concurrent family effects are correlated; additive summation can double-count a large day.
- Holiday/event behavior is excluded rather than modeled; this framework cannot predict flagship-event peaks.
- Pricing, duration, exact segment, album phase, LBP peak, and audience size are incomplete in the wide source.
- Wager, gem usage, and segment-level validation return **insufficient evidence**.
- Family-level direction can be unstable where occurrences are sparse or systematically placed on one weekday/context.

## Calibration implication

Eligibility and expected ranges in `PREDICTION_AND_OPTIMIZATION.md` must use these observed errors. A recommendation cannot claim precision tighter than the demonstrated out-of-sample error/range.

Machine-readable results: `backtest_results.json`.
