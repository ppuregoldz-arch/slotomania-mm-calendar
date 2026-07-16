# DWH Reference — playtika_dwh (Vertica, SM) — Live via mcp-alchemy

> חיבור חי דרך MCP `user-mcp-alchemy-sm` (`execute_query`, `filter_table_names`, `schema_definitions`, `all_table_names`). מקור מלא: `dwh_context/` (per-squad queries + business context). ⚠️ verticalb = load balancer — קריאה ראשונה עלולה ליפול, retry פותר.

## טבלאות מפתח למוניטיזציה
| טבלה | גרעין | שימוש |
|---|---|---|
| **`agg.agg_sm_daily_users_stats`** | user×calc_date | ⭐ מקור אמת: `daily_Net_revenue`, `spins`, `bet_coins`, `win_coins`, `balance_end_day`, `gems_end_of_day_balance`, `actual_median_bet`, tiers. DAU/רבניו/wager/בלנסים. |
| `agg.agg_sm_daily_promotion_stats` | user×promo_date | קונברז'ן לפי promo_date. |
| **`dwh.sm_fact_payments`** | txn | תשלומים — **חובה `tran_status_id=2`** (+`is_test=0`,`artificial_ind=0`); join `sm_draft.SM_DIM_Products` על `sku_id`+`transaction_source_type_id` → `Product_Name`. |
| `dwh.fact_sm_user_offer_history_po2` | offer state | מחזור הצעה (IMPRESSION/PURCHASE/CLOSED, `offer_name`, `price`, `is_rolling_offer`). |
| `dwh.fact_sm_spin_history_kafka` | spin | `bet_amount`/`win_amount`/`machine_type_id`. |
| `dwh.fact_sm_bonus_history` / `dwh.fact_sm_goods_service_data` | bonus/goods | פרסים (קלפים/hammers) שחולקו. |
| `dwh.sm_fact_internal_purchases` | gems spend | `currency_id=10000`; join `dim_transaction_source_type` → קטגוריית מקור ג'מס. |

## כללי זהב (HARD)
- **רבניו**: תמיד `agg...daily_Net_revenue`; ב-payments חובה `tran_status_id=2` (אחרת ~25× ניפוח).
- **Two-step aggregation** לממוצעים (יומי → AVG). **Conversion = decimal** (`payers/dau`).
- **החרגות סטנדרטיות**: `user_id>0`, לא Iraq, לא test (journey step 539265), לא Playtika employees (`dwh.playtika_users`).
- **היפר-אינפלציה**: bet/win/balance בטריליונים+ = נורמלי.

## שאילתות קנוניות
**Trend יומי (DAU/רבניו/משלמים):**
```sql
SELECT calc_date, COUNT(DISTINCT user_id) dau, SUM(daily_Net_revenue) rev,
       COUNT(DISTINCT CASE WHEN daily_Net_revenue>0 THEN user_id END) payers
FROM agg.agg_sm_daily_users_stats WHERE calc_date >= CURRENT_DATE-30 AND user_id>0
GROUP BY calc_date ORDER BY calc_date;
```
**Revenue by Product (30d):**
```sql
SELECT prod.Product_Name, SUM(p.net_amount) net_rev, COUNT(DISTINCT p.user_id) payers
FROM dwh.sm_fact_payments p LEFT JOIN sm_draft.SM_DIM_Products prod
  ON p.sku_id=prod.sku_id AND p.transaction_source_type_id=prod.transaction_source_type_id
WHERE p.tran_status_id=2 AND p.is_test=0 AND p.artificial_ind=0 AND p.tran_date>=CURRENT_DATE-30
GROUP BY prod.Product_Name ORDER BY net_rev DESC;
```

## Baseline חי (מדידה אחרונה — יוני-יולי 2026, 21-30 יום)
- **DAU** ≈ 405-413K/יום · **רבניו** ≈ $620K/יום (טווח $515K-$872K) · **משלמים** ≈ 27K/יום · **conversion** ≈ 6.6% · **ARPU** ≈ $1.54 · **ARPPU** ≈ $23.
- **רבניו לפי מוצר ($/יום)**: MGAPP ~$181K · Sticky Bundle/DD ~$119K · Payment Page ~$58K · Gems ~$39K · Rolling ~$28K · Reveal ~$25K · Clan Dash Bundle/Prize Mania/Buy All/Decoy נמוכים יותר. זהו דירוג מוצר היסטורי, לא אימות סיבתי של חיזוי; ראה `prediction/PREDICTION_AND_OPTIMIZATION.md`.
- **משחקיות/Velocity**: Spinners ~283K/יום (~70% מ-DAU) · **Velocity (spins/spinner) ~765-874/יום** · Sessions ~4.2/user. Velocity גבוה בימי MES/אירוע (6/21,6/22,6/29). ⚠️ Win-rate ו-avg-bet תנודתיים תחת היפר-אינפלציה — לא KPI יומי אמין.
- ⭐ **ריכוז רבניו לפי Tier (7 ימים)**: Tiers 6-7 = **~7% מהמשתמשים אך ~75% מהרבניו** (T6 $1.34M, T7 $1.91M/שבוע; T7=10K משתמשים). avg spins עולה עם Tier (T1 164 → T7 1282). **ירידת משחקיות בטירים 6-7 = דגל אדום** (מנוע הרבניו). מוצג בטאב "Game Health" בדשבורד.

---
**עודכן:** יולי 2026 · מקור: DWH חי + `dwh_context/`.
