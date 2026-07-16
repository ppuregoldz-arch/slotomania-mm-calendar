---
name: Slotomania Data Knowledge Base (Main Tables) — Reference Only
description: >
  Reference-only knowledge base for key Slotomania tables captured from internal docs/screenshots.
  NOT authoritative. The source of truth is our live queries and validated results.
  Columns listed here are **not** guaranteed to be used in production. Always verify.
globs:
  - "**/*.sql"
  - "**/*analysis*"
  - "**/*query*"
  - "**/*.md"
alwaysApply: false
---

> **Purpose & Scope**
> - This summarizes *some* main Slotomania tables you shared.
> - Many columns exist but are not used; treat everything here as **informational**.
> - The real source of knowledge is our **actual queries** and their validated outputs.
> - Before using any column that isn't already in our queries, **check values and confirm with a BA**.

## Usage Verification Checklist (do this before adopting a column)
1. Pull a small sample by date/user to inspect raw values.
2. Check NULL rate, cardinality, units, and expected ranges.
3. Cross-validate with a related fact/dimension or event.
4. Ask the feature owner/BA whether this column is used or deprecated.
5. Add validation notes (ID/time window + manual math) next to the query.

---

# Table Catalog (selected highlights from docs/screenshots)
Notes:
- Joins below indicate commonly referenced dimensions.
- Unless stated otherwise, use `environment_id = 1` and `game_type_id = 2 (SM)` when applicable.
- **Headings say “Selected column notes (from docs — validate usage)”** to emphasize that these are not “frequently used”.

---

## 1) `sm_fact_payments`  — External payments
**What it stores:** External (real-money) payment activity and status updates.  
**Primary identifiers:** `tran_id`, `tran_ticket`, `user_id`, `tran_ts/tran_date`  
**Partitions/filters:** prefer `tran_date` (creation date).

**Selected column notes (from docs — validate usage):**
- Keys & dates: `tran_id`, `tran_ticket`, `tran_ts`, `tran_date`
- User & context: `user_id`, `session_id`, `client_type_id`, `platform_id`
- Amounts: `transaction_amount`, `received_tran_amount`, `tax_amount`, `net_amount = transaction_amount - tax_amount`, `gross_amount`, `a.cost_before_price_cut` (if NOT NULL then there was price cut - original gross amount)
- Currency: `currency_id` (104=USD), `received_currency_id` (104=USD, 0=Slot Bucks), ISO fields
- Status: `tran_status_id` (1=in progress, 2=approved, 3=canceled, 4=declined, 5=charge back, 6=refunded, 7=failed), `tran_status_reason_id`, `tran_status_updated_ts`, `tran_status_updated_by`
- Product & page: `sku_id`, `payment_page_id`, `payment_method_id`, `payment_page_type_id`
- Flags: `is_test`, `artificial_ind` (0=real), `test_group_id`, `segment_id`, `page_option_id`, `in_club`, `is_playtika_user`, `is_ftd_platform`, `is_std_platform`, `is_user_migrated`

**Cautions:** `local_currency_*` and `gift_card_pin` often unused; confirm before use. Use `tran_ticket` to connect to related offer/bonus records when relevant.

---

## 2) `sm_fact_internal_purchases`  — Internal (gems/fun points) purchases
**What it stores:** In‑game purchases using internal currencies.  
**Primary identifiers:** `purchase_id`, `user_id`, `timestamp`

**Selected column notes (from docs — validate usage):**
- Keys & dates: `purchase_id`, `timestamp`, `insert_ts`
- User & session: `user_id`, `session_id`, `client_type_id`, `platform_id`
- Product & cost: `sku_id`, `amount` (quantity/progress), `cost` (in gems), `dollar_value` (0 for internal), `sku_id_2`/`sku_id_2_amount` (fun points)
- Source & flags: `transaction_source_type_id`, `is_ftd_platform`, `page_attribute_id`
- Link-outs: `tran_ids` (external payment if topped-up mid-flow)

**Cautions:** Several `inner_*`/`origin` fields marked N/R; validate meaning of `amount` per SKU type.

---

## 3) `dwh.fact_sm_user_offer_history_po2`  — Offer lifecycle
**What it stores:** Offer creation, impression, purchase, close.  
**Primary identifiers:** `offer_id`, `user_id`, `offer_status_ts`

**Selected column notes (from docs — validate usage):**
- State: `offer_status_id` (CREATED / CLOSED / PURCHASE / IMPRESSION), `offer_status_detail`/`state_details`
- Pricing & window: `price`, `duration_in_seconds`, `is_rolling_offer`
- Context: `platform_id`, `tier_id`, `level_id`, `offer_type_id`, `source`
- Traceability: `tran_ticket`, `page_resolve_request_id`, `source_correlation_id`, `correlation_id`
- Names: `offer_name`

**Cautions:** Use `tran_ticket` to verify purchases; impressions may be noisy—filter by state.

**Rolling Offer impressions (PO2):** Use `offer_status_id = 'IMPRESSION'` and `offer_name ilike '%rolling offer%'` (name may include extra words). Do **not** rely on `is_rolling_offer = true` alone for RO impression counts—flag and naming can diverge (e.g. promo-day PO2 names without the substring “rolling offer”). Payments for RO still use `SM_DIM_Products.product_name = 'Rolling Offer'`. See `sql/rolling_offer_impressions_and_avg_trx_by_promo_date_utc_hours_11_12_13.sql`.

---

## 4) `agg.agg_sm_daily_promotion_stats` — Promo Date User Aggregation  
**What it stores:** Daily user metrics aggregated by promo_date instead of calc_date  
**Primary identifiers:** `user_id`, `promo_date`  
**Key usage:** Use for promo date conversion analysis, DAU by promo date  
**DAU Pattern:** `COUNT(DISTINCT user_id)` grouped by promo_date  
**Conversion Formula:** `feature_users / dau` (decimal, not percentage)

---

## 5) `dwh.fact_sm_sessions_kafka`  — Session starts (Kafka)
**What it stores:** Session start with device/channel attributes.  
**Primary identifiers:** `session_id`, `user_id`, `session_creation_ts/session_creation_date`

**Selected column notes (from docs — validate usage):**
- Identity: `user_id`, `client_type_id`, `platform_id`, `sn_type_id`, `user_sn_id`
- Device/network: `device`, `os`, `version`, `carrier`, `udid`, `guid`, `ip`, `user_agent`
- Marketing: `channel`, `affiliate`, `campaign`, `link_channel`, `led_page_url`
- Gameplay: `first_session`, `friends_count`
- Snapshot: `user_balance`, `user_level`, `user_experience`, `is_paying_user`
- Ops: `insert_ts`, `last_updated_ts`, `environment_id`, `game_type_id`

**Cautions:** Many optional fields (`timezone`, `locale`, `old_tier_id`) may be NULL—inspect first.

---

## 5) `dwh.fact_sm_bonus_history`  — Bonuses granted
**What it stores:** All types of bonus awards.  
**Primary identifiers:** `user_id`, `bonus_ts` (+ optional `transaction_ticket`).

**Selected column notes (from docs — validate usage):**
- Core: `bonus_type_id`, `bonus_amount`, `user_new_balance`, `platform_id`, `session_id`
- Snapshot: `user_level`, `tier_id`, `decorated_tier_id`, `recent_player`
- Event/meta: `reward_request_id`, `parent_reward_request_id`, `reward_id`, `event_id`, `journey_step_id`, `job_id`, `source`, `machine_id`, `sku_id`, `blast_game_id/board_id`, `snl_event_id`
- Multipliers: `multiplier`, `turbo`, `cashback_multiplier`, various feature-specific multipliers
- Timestamps: `bonus_date`, `insert_ts`

**Cautions:** Some fields explicitly “not working for hourly bonuses” or feature-specific; verify per feature.

---

## 6) `dwh.Sm_User_Profile`  — User profile (aggregated)
**What it stores:** Latest user profile snapshot.  
**Primary key:** `user_id`

**Selected column notes (from docs — validate usage):**
- Identity & install: `user_id`, `installation_ts`, `first_login_ts`, `is_playtika_user`, `is_fb_uninstalled`
- Status: `user_level`, `tier_id`, `status_points`, `user_experience`
- Payments/LTV: `count_payments`, `is_paying`, `sum_success_tran_amount`, `sum_net_amount`, `first_transaction_*`, `last_transaction_*`
- Engagement: `last_login_ts`, `last_click_ts`, `favorite_channel`, `last_platform_id`
- Piggy bank: `piggybank_balance`, `piggybank_cap`, `piggybank_cap_date`
- Comms: `email_send`, `email_opens`, `email_click`, `email_ctr`, `push_mobile_received/opened/ctr`
- Risk/ops: `is_banned`, `is_merged`, `ip_country`

**Cautions:** As an **agg**, not suitable for event timing without care—prefer facts for timelines.

---

## 7) `dwh.fact_sm_spin_history_kafka`  — Spin outcomes (Kafka)
**What it stores:** Per-spin outcomes and machine/feature metadata.  
**Primary identifiers:** `guid`, `user_id`, `session_id`, `spin_ts`  
**Partition:** `spin_date`

**Selected column notes (from docs — validate usage):**
- Context: `platform_id`, `client_type_id`, `session_id`, `xml_id`, `machine_type_id`
- Bet & win: `bet_amount`, `actualBetAmount`, `win_amount`, `bonus_multiplier`, `bonus_won`, `free_spin_count`, `free_spin_win_sum`
- Snapshot: `user_level`, `user_experience`, `balance`, `piggybank_balance`
- Feature flags: `fast_spin`, `auto_spin`, `is_mini_game`, `bonus_restored`
- Machine-specific examples: `route`, `feature_upgrade_*`, `antebet_*`, `msp_state`, `applied_cannonball_*`, `dynamites_reel_*`, etc.

**Cautions:** Many columns are feature/machine-specific—verify scope before analysis. Filter with half‑open dates for pruning.

---

## 8) `dwh.fact_sm_goods_service_data`  — Granted goods (sku_id != 0)
**What it stores:** Delivery of goods to users.  
**Primary identifiers:** `user_id`, `sku_id`, `bonus_ts`

**Selected column notes (from docs — validate usage):**
- Core: `bonus_amount`, `reward_ts/bonus_ts`, `user_level`, `tier_id`, `decorated_tier_id`
- Traceability: `reward_request_id`, `parent_reward_request_id`, `request_id`, `transaction_id`, `event_id`, `generate_watermark_spin_guid`, `gift_card_id`
- Collections/Journeys: `collectibles_album_id`, `collectibles_set_id`, `mission_step_id`, `journey_id/journey_step_id/job_id`
- Context: `client_type_id`, `platform_id`, `game_type`, `snl_*`, `blast_game_id`, `game_uid`
- Meta: `sku_data`, `event_type`, `event_date`, `board_multiplier`, `bs_sys_process_ts`

**Cautions:** Some columns are `NULL`/not relevant in practice—inspect distributions first.

---

# Final Notes
- This file is **reference-only**. It does not imply “frequent usage” of any column.
- When a column here is **not** in our current queries, treat it as *unconfirmed*. Validate first, then amend this doc with notes.
- For column usage discovery, we can parse our SQL repo to produce a frequency report of columns actually referenced.
