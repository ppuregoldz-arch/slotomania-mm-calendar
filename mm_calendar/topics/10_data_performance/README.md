# 10 — Data · Performance · Patterns

## מתי נכנסים
- לבחור **וריאציה** בתוך מסלול (לא לשבור caps)
- להבין יום-בשבוע / עומק vs רוחב
- לכייל tie-breaks בבילדר (`calibrate_model.py`)

## קבצים
| קובץ | שימוש |
|------|--------|
| `performance/README.md` | אינדקס קנוני לפי Main KPI + variant |
| `performance/instances/promo_instances.jsonl` | instance אחד לכל שורה, Apr–Jul 2026 |
| `measurement/MEASUREMENT_METHODOLOGY.md` | baseline, confidence, causality, provenance |
| `smart_calendar_insights.md` | ליפטים אמיתיים (מנועים עצמאיים vs מותני חג) |
| `promo_revenue_analysis.md` | וריאציה מנצחת per lane |
| `performance_benchmarks.md` | הכנסה per feature |
| `patterns_derived.md` | תדירות/ריווח מהבורד |
| `relationships_deep.md` | DOW, שבוע בחודש, עומק/רוחב |
| `prediction/PREDICTION_AND_OPTIMIZATION.md` | framework אחרי backtest + eligibility |
| `prediction/BACKTEST_RESULTS.md` | שגיאות out-of-sample ומקרי כשל |
| `daily_mm_reports.md` | מה עבד בפועל בערב |
| `dwh_reference.md` | שאילתות Vertica (אם MCP זמין) |

## כלל השוואה
**Same-DOW trailing ≥20 ימים מלאים** — לא יום בודד מ-%Difference בדשבורד. תוצאה יומית עם כמה פרומואים = correlation, לא attributed lift.

## דאטה מקומית
`performance/instances/promo_instances.jsonl` · `data/model_calibration.json` · `data/real_months.json` · `data/wide_revenue_pu.json`

## קרא עומק
`deep_research_insights.md` · `boosted_gemback_impact.md`
