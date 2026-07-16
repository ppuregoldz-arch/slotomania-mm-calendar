# Dice Deluxe - Queries

**Note**: This file contains only queries provided by the user, not queries created during conversations.

## Query Inventory

### 1. Dice Deluxe Conversion Analysis
**Purpose**: Track conversion from x150 free Dice hits to Dice Deluxe purchases  
**Category**: Conversion Analysis / Performance Tracking  
**Business Metric**: Measures the core conversion funnel from free jackpot experience to premium upgrade

```sql
select
    'Dice'                                                                          as                   product_name,
    a.week_start,
    coalesce(cz_range, '0-4.99')                                                    as                   cz_range,
    case when b.b_user_id is not null then 1 else 0 end                             as                   is_PU_30d,
    sum(case when bonus_type_id = 66 and face_multiplier = 150 then 1 else 0 end)   as                   weekly_imp_events,
    count(distinct case
                       when bonus_type_id = 66 and face_multiplier = 150 then user_id
                       else null end)                                               as                   weekly_imp_users,
    count(distinct case when bonus_type_id = 587 and a.tran_id is not null then d.tran_id else null end) weekly_trx,
    count(distinct case
                       when bonus_type_id = 587 and a.tran_id is not null then d_user_id
                       else null end)                                                                    weekly_PUs,

    sum(coalesce(gross_amount, 0))                                                  as                   weekly_gross_amount,
    sum(coalesce(net_amount, 0))                                                    as                   weekly_net_amount,
    (count(distinct case
                        when bonus_type_id = 587 and a.tran_id is not null then d_user_id
                        else null end)) / (count(distinct case
                                                              when bonus_type_id = 66 and face_multiplier = 150
                                                                  then user_id
                                                              else null end))       as                   weekly_cov_users,
    (count(distinct d.tran_id)) /
    (sum(case when bonus_type_id = 66 and face_multiplier = 150 then 1 else 0 end)) as                   weekly_cov_events


/*dice deluxe tbl*/
from (select distinct
          event_date,
          event_ts,
          user_id,
          face_multiplier,
          bonus_type_id,
          tran_id,
          date_trunc('week', event_date)::date as week_start
      from dwh.sm_fact_dice_booster_bonus_data
      where 1 = 1
        and user_id not in (select distinct user_id from dwh.playtika_users)
        and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
        and event_date >= '2026-02-01'::date) a
         /*users with up to 3 imp per week*/
         join (select distinct
                   week_start,
                   user_id as up_to_3_imp_user_id
               from (select
                         user_id,
                         date_trunc('week', event_date)::date as week_start,
                         count(*)                             as free_dice_events
                     from dwh.sm_fact_dice_booster_bonus_data
                     where 1 = 1
                       and user_id not in (select distinct user_id from dwh.playtika_users)
                       and user_id not in
                           (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
                       and bonus_type_id = 66
                         and face_multiplier=150
--         and event_date >= '2026-02-01'::date
                       and event_date >= '2026-02-01'::date
                     group by 1, 2
                     having count(*) <= 3) A) u
              on a.user_id = u.up_to_3_imp_user_id and a.week_start = u.week_start
         /*PU last 30 days dim*/
         left join (select distinct
                        user_id as b_user_id
                    from agg.agg_sm_daily_users_stats
                    where 1 = 1
                      and calc_date >= current_date - 30
                      and daily_gross_rev > 0) b
                   on a.user_id = b.b_user_id
    /*cz buckets*/
         left join (select
                        user_id as c_user_id,
                        event_date_datamining,
                        cz_price_cut_test,
                        case
                            when coalesce(cz_price_cut_test, 0) < 5 then '0-4.99'
                            when cz_price_cut_test < 10 then '5-9.99'
                            when cz_price_cut_test < 25 then '10-24.99'
                            when cz_price_cut_test < 50 then '25-49.99'
                            when cz_price_cut_test < 100 then '50-99.99'
                            when cz_price_cut_test >= 100 then '100+'
                            end as cz_range
                    from dwh.sm_user_profile_datamining_snapshot
                    where 1 = 1
                      and event_date_datamining >= '2026-02-01'::date) c
                   on a.user_id = c.c_user_id and a.event_date = c.event_date_datamining
/*payments*/
         left join (SELECT
                        Product_Name,
                        user_id as d_user_id,
                        tran_id,
                        gross_amount,
                        net_amount
                    from dwh.sm_fact_payments a
                             left join sm_draft.SM_DIM_Products b
                                       on a.sku_id = b.sku_id and
                                          a.transaction_source_type_id = b.transaction_source_type_id
                    where 1 = 1
                      and tran_status_id = 2
                      and artificial_ind = 0
                      and is_test = 0
                      and user_id > 0
                      and Product_Name = 'Dice Deluxe'
                      and tran_date >= '2026-02-01'::date) d
                   on a.user_id = d.d_user_id and a.tran_id = d.tran_id

group by 1, 2, 3, 4;
```

## Query Analysis & Key Insights

### **Core Conversion Metrics Tracked:**
- **Impression Events**: Weekly x150 hits (bonus_type_id = 66, face_multiplier = 150)
- **Impression Users**: Distinct users who hit x150 jackpot  
- **Purchase Transactions**: Dice Deluxe purchases (bonus_type_id = 587)
- **Purchase Users**: Distinct users who bought Dice Deluxe
- **Conversion Rates**: Users and events conversion from x150 to purchase

### **Business Intelligence Dimensions:**
- **Weekly Analysis**: Time-series tracking by week_start
- **CZ Segmentation**: 6 spending buckets (0-4.99 through 100+)
- **Payer Classification**: is_PU_30d flag for recent paying users
- **Revenue Tracking**: Gross and net amounts for Dice Deluxe purchases

### **Key Business Rules Identified:**

#### **Bonus Type IDs**
- **66**: Free Dice rolls (including x150 jackpot hits)
- **587**: Dice Deluxe purchases (premium upgrade)

#### **Quality Filters**
- **User Exclusions**: Playtika internal users and journey step 539265 users removed
- **Frequency Cap**: Users limited to ≤3 x150 impressions per week (quality control)
- **Payment Validation**: Standard payment filters (status=2, non-test, non-artificial)

#### **CZ Spending Buckets**
- 0-4.99, 5-9.99, 10-24.99, 25-49.99, 50-99.99, 100+ (based on cz_price_cut_test)

### **Performance Analysis Framework**
- **weekly_cov_users**: User-level conversion rate (buyers/impressions) 
- **weekly_cov_events**: Event-level conversion rate (purchases/x150 hits)
- **Revenue per Conversion**: Weekly gross/net amounts per converting user
- **Segment Performance**: Conversion rates by CZ bucket and payer status

### **Key Tables Used**
- `dwh.sm_fact_dice_booster_bonus_data` - Core Dice events and multiplier tracking
- `dwh.sm_fact_payments` + `sm_draft.SM_DIM_Products` - Dice Deluxe purchase transactions
- `dwh.sm_user_profile_datamining_snapshot` - CZ segmentation  
- `agg.agg_sm_daily_users_stats` - Recent payer classification
- `dwh.playtika_users` + `dwh.sm_fact_journey_state_notifications` - User exclusions

### 2. Dice Deluxe Price Validation & Test Group Check
**Purpose**: Validate pricing accuracy and ensure only test users receive Dice Deluxe  
**Category**: Gatekeeping / Quality Assurance  
**Business Metric**: Price integrity and test group compliance validation

```sql
/*price check & only test receiving*/

select *,
       case when group_name = 'Test' then 'ok' else 'wrong' end                    as only_test_users_receiving_dice_deluxe,
       case when round(gross_amount) = round(config_price) then 'ok' else null end as price_check
/*payments*/
from (SELECT
          tran_ts,
          tran_date,
          user_id,
          gross_amount,
--           price,
          case
              when Product_Name = 'Payment Page' and payment_page_type_id = 30 then 'Payment Page'
              when Product_Name = 'Payment Page' and payment_page_type_id != 30 then 'ROOC'
              when Product_Name = 'Gems' and payment_page_type_id = 62 then 'Gems Payemnt Page'
              when Product_Name = 'Gems' and payment_page_type_id != 62 then 'ROOG'
              else Product_Name end as Product_Name

      from dwh.sm_fact_payments a
               left join sm_draft.SM_DIM_Products b
                         on a.sku_id = b.sku_id and a.transaction_source_type_id = b.transaction_source_type_id
      where 1 = 1
        and tran_status_id = 2
        and artificial_ind = 0
        and is_test = 0
        and user_id > 0
        and Product_Name = 'Dice Deluxe'
        and user_id not in (select distinct user_id from dwh.playtika_users)
        and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
        and tran_ts >= '2026-01-15 12:50:00') a
/*CZ*/
         left join (SELECT
                        event_date_datamining,
                        user_id as b_user_id,
                        DPU_Segment,
                        cz_price_cut_test,
                        case
                            when cz_price_cut_test < 2 then '0-1.99'
                            when cz_price_cut_test < 3 then '2-2.99'
                            when cz_price_cut_test < 5 then '3-4.99'
                            when cz_price_cut_test < 7 then '5-6.99'
                            when cz_price_cut_test < 10 then '7-9.99'
                            when cz_price_cut_test < 15 then '10-14.99'
                            when cz_price_cut_test < 20 then '15-19.99'
                            when cz_price_cut_test < 25 then '20-24.99'
                            when cz_price_cut_test < 30 then '25-29.99'
                            when cz_price_cut_test < 40 then '30-39.99'
                            when cz_price_cut_test < 50 then '40-49.99'
                            when cz_price_cut_test < 60 then '50-59.99'
                            when cz_price_cut_test < 70 then '60-69.99'
                            when cz_price_cut_test < 80 then '70-79.99'
                            when cz_price_cut_test < 90 then '80-89.99'
                            when cz_price_cut_test < 100 then '90-99.99'
                            when cz_price_cut_test < 120 then '100-119.99'
                            when cz_price_cut_test < 140 then '120-139.99'
                            when cz_price_cut_test < 160 then '140-159.99'
                            when cz_price_cut_test < 180 then '160-179.99'
                            when cz_price_cut_test < 200 then '180-199.99'
                            when cz_price_cut_test < 250 then '200-249.99'
                            when cz_price_cut_test < 300 then '250-299.99'
                            when cz_price_cut_test < 400 then '300-399.99'
                            when cz_price_cut_test < 1000 then '400-999.99'
                            when cz_price_cut_test >= 1000 then '1000+'
                            end as config_cz_range
                    from dwh.sm_user_profile_datamining_snapshot
                    where 1 = 1
                      and event_date_datamining >= current_date - 1
                    group by 1, 2, 3, 4, 5) b
                   on a.user_id = b.b_user_id and a.tran_date = b.event_date_datamining
/*test groups*/
         left join (select
                        a.user_id as t_user_id,
                        group_name
                    from sm_ds.abtest_user_allocations a
                             left join sm_ds.abtest_dim_test t
                                       on a.test_id = t.ab_test_id
                             left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                    where 1 = 1
                      and test_id = 'HaJDndJpCn') t
                   on a.user_id = t.t_user_id
/*prices - config*/
         left join (select *
                    from sm_draft.dice_booster_price_config_14_01) c
                   on b.cz_price_cut_test between c.cz_from and c.cz_to;
```

### 3. Dice Deluxe Average Multiplier Analysis
**Purpose**: Analyze average multiplier values for Dice Deluxe rolls  
**Category**: Performance Analysis / Game Balance  
**Business Metric**: Multiplier distribution and average payout validation

```sql
/*avg - Dice Deluxe multiplier*/
-- Ex- 762.6

select
    avg(face_multiplier) as avg_multiplier,
    count(*)             as events
-- select *
from dwh.sm_fact_dice_booster_bonus_data a
/*test groups*/
         left join (select
                        a.user_id as t_user_id,
                        group_name
                    from sm_ds.abtest_user_allocations a
                             left join sm_ds.abtest_dim_test t
                                       on a.test_id = t.ab_test_id
                             left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                    where 1 = 1
                      and test_id = 'ApQib3w5Xq') t
                   on a.user_id = t.t_user_id
where 1 = 1
  and tran_id is not null
  and user_id not in (select distinct user_id from dwh.playtika_users)
  and user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
  and event_ts >= '2026-01-15 12:50:00';
```

### 4. Free Dice Fairness Analysis - Star (x150) Hit Rate
**Purpose**: Validate fairness of free Dice rolls and x150 jackpot frequency  
**Category**: Game Balance / Fairness Validation  
**Business Metric**: Star win ratio per user to ensure fair probability distribution

```sql
/*dice freemium - how many rolls it takes to fall on the star- FAIR DICE*/
select
    user_id,
    parent_reward_request_id,
    sum(case when face_multiplier = 150 then 1 else 0 end)              as star_wins_cnt,
    sum(case when face_multiplier != 150 then 1 else 0 end)             as NOT_star_wins_cnt,
    count(*)                                                            as overall_rollings,
    (sum(case when face_multiplier = 150 then 1 else 0 end)) / count(*) as star_wins_ratio_per_dice
from dwh.sm_fact_dice_booster_bonus_data a
/*test groups*/
         left join (select
                        a.user_id as t_user_id,
                        group_name
                    from sm_ds.abtest_user_allocations a
                             left join sm_ds.abtest_dim_test t
                                       on a.test_id = t.ab_test_id
                             left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                    where 1 = 1
                      and test_id = 'HaJDndJpCn') t
                   on a.user_id = t.t_user_id
where 1 = 1
  and event_ts >= '2026-01-15 12:00:00'
  and tran_id is null
group by 1, 2;
```

### 5. Comprehensive Dice Conversion Rate Analysis
**Purpose**: Complete funnel analysis from free Dice to Dice Deluxe with A/B testing metrics  
**Category**: A/B Testing / Conversion Analysis  
**Business Metric**: Multi-dimensional conversion tracking with DAU normalization

```sql
/*Dice conversion rate*/

select
    a.group_name,
    a.promo_date,
    a.allocation_percentage,
    max(DAU)                                                                        as DAU,
    count(case when Dice_type = 'Dice free' then user_id else null end)             as events_dice_free,
    count(case when Dice_type = 'Dice Deluxe' then user_id else null end)           as events_dice_deluxe,
    count(case when Dice_type_star = 'Dice free - Star' then user_id else null end) as events_dice_free_star,
    count(distinct case
                       when Dice_type = 'Dice free' then user_id
                       else null end)                                               as distinct_users_dice_free,
    count(distinct case
                       when Dice_type = 'Dice Deluxe' then user_id
                       else null end)                                               as distinct_users_dice_deluxe,
    count(distinct case
                       when Dice_type_star = 'Dice free - Star' then user_id
                       else null end)                                               as distinct_users_dice_free_star,
    count(case when Dice_type = 'Dice Deluxe' then tran_id else null end)           as trx_dice_deluxe,
    sum(gross_amount)                                                               as gross_amount_dice_deluxe

from (select
          a.*,
          group_name,
          allocation_percentage,
          b.gross_amount,
          case
              when bonus_type_id = 66 then 'Dice free'
              when bonus_type_id = 587 and b.tran_id is not null then 'Dice Deluxe'
              else null end                                                        as Dice_type,
          case
              when bonus_type_id = 66 and face_multiplier = 150 then 'Dice free - Star'
              when bonus_type_id = 66 and face_multiplier != 150 then 'Dice free - not Star'
              when bonus_type_id = 587 and b.tran_id is not null then 'Dice Deluxe'
              else null end                                                        as Dice_type_star,
          case when bonus_type_id = 66 and face_multiplier = 150 then 1 else 0 end as is_win_star_free_Dice
/*Dice table- free & deluxe*/
      from (select
                user_id,
                event_ts,
                date(event_ts::timestamp AT TIME ZONE 'UTC' at
                    time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                event_date,
                bonus_type_id,
                tran_id,
                bonus_amount,
                face_multiplier

            from dwh.sm_fact_dice_booster_bonus_data
            where 1 = 1
              and user_id not in (select distinct user_id from dwh.playtika_users)
              and user_id not in
                  (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
              and event_ts >= '2026-01-15 12:00:00') a
/*test groups*/
               left join (select
                              a.user_id as t_user_id,
                              group_name,
                              allocation_percentage
                          from sm_ds.abtest_user_allocations a
                                   left join sm_ds.abtest_dim_test t
                                             on a.test_id = t.ab_test_id
                                   left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                          where 1 = 1
                            and test_id = 'HaJDndJpCn') t
                         on a.user_id = t.t_user_id
/*payments - dice purchases*/
               left join (SELECT
                              tran_ts,
                              user_id,
                              payment_quantity,
                              tran_id,
                              tran_date,
                              date(tran_ts::timestamp AT TIME ZONE 'UTC' at
                                  time zone 'Asia/Jerusalem' - interval '14 hours') as promo_date,
                              gross_amount
--           price
                          from dwh.sm_fact_all_payments a
                                   left join sm_draft.SM_DIM_Products b
                                             on a.sku_id = b.sku_id and
                                                a.transaction_source_type_id = b.transaction_source_type_id
                          where 1 = 1
                            and tran_status_id = 2
                            and artificial_ind = 0
                            and is_test = 0
                            and user_id > 0
                            and tran_ts >= '2026-01-15 12:00:00'
                            and Product_Name = 'Dice Deluxe') b
                         on a.user_id = b.user_id and a.tran_id = b.tran_id) A
/*DAU per group*/
         left join (select
                        promo_date,
                        group_name,
                        count(distinct user_id) as DAU
                    from agg.agg_sm_daily_promotion_stats a
/*test groups*/
                             left join (select
                                            a.user_id as t_user_id,
                                            group_name
                                        from sm_ds.abtest_user_allocations a
                                                 left join sm_ds.abtest_dim_test t
                                                           on a.test_id = t.ab_test_id
                                                 left join sm_ds.abtest_dim_group g on a.group_test_id = g.test_group_id
                                        where 1 = 1
                                          and test_id = 'HaJDndJpCn') t
                                       on a.user_id = t.t_user_id
                    where 1 = 1
                      and promo_date >= '2026-01-14'::date
                    group by 1, 2) b
                   on a.promo_date = b.promo_date and a.group_name = b.group_name
group by 1, 2, 3;
```

## Enhanced Technical Analysis & Table Structures

### **Key Table Relationships Revealed:**

#### **Core Dice Events Table**
- **`dwh.sm_fact_dice_booster_bonus_data`**: Central events table
  - **bonus_type_id**: `66` (Free Dice), `587` (Dice Deluxe purchases)
  - **face_multiplier**: Dice roll results (1-5, 150 for jackpot, 762.6 avg for Deluxe)
  - **tran_id**: Links to payment transactions when present
  - **parent_reward_request_id**: Groups multiple rolls per session

#### **A/B Testing Framework**
- **Test Infrastructure**: `sm_ds.abtest_user_allocations` + `abtest_dim_test` + `abtest_dim_group`
- **Current Test IDs**:
  - **`HaJDndJpCn`**: Main Dice Deluxe test (Test vs Control groups)
  - **`ApQib3w5Xq`**: Dice multiplier analysis test
- **Group Allocation**: `allocation_percentage` tracks test group distribution

#### **Pricing & Configuration**
- **Price Config Table**: `sm_draft.dice_booster_price_config_14_01`
- **Detailed CZ Buckets**: 24 granular spending segments (0-1.99 through 1000+)
- **DPU Segmentation**: Available in datamining snapshot for enhanced user classification

#### **Payment Integration**
- **Payment Tables**: `dwh.sm_fact_payments` + `dwh.sm_fact_all_payments`
- **Product Classification**: Complex logic for Payment Page, ROOC, Gems Payment Page, ROOG
- **Payment Page Type IDs**: `30` (Payment Page), `62` (Gems Payment Page)

### **Advanced Business Logic Patterns:**

#### **Promo Date Calculation**
- **Standard Pattern**: `date(timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '14 hours')`
- **Business Hours Alignment**: 14-hour offset aligns with business day (10 AM Jerusalem time)

#### **Fairness Validation Framework**
- **Star Hit Rate Tracking**: Individual user x150 frequency analysis
- **Expected Probability**: 1/6 = 16.67% for fair dice
- **Multiplier Distribution**: Avg ~762.6 for Dice Deluxe (premium experience validation)

#### **Multi-Dimensional Conversion Tracking**
- **Events vs Users**: Separate tracking for frequency and reach
- **Star Segmentation**: Free Dice users split by x150 experience
- **DAU Normalization**: Conversion rates adjusted by daily active users per test group

### **Key Configuration Tables**
- **`sm_draft.dice_booster_price_config_14_01`**: CZ-based pricing matrix
- **`dwh.sm_user_profile_datamining_snapshot`**: User segmentation + CZ buckets
- **`sm_ds.abtest_*`**: Complete A/B testing framework
- **`agg.agg_sm_daily_promotion_stats`**: DAU tracking per test group

---
**Source**: User-provided comprehensive Dice Deluxe analytics queries covering pricing validation, A/B testing, fairness analysis, and conversion tracking with detailed table structure insights.