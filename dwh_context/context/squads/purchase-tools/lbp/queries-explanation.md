# LBP - Queries

**Note**: This file contains only queries provided by the user, not queries created during conversations.

## Query Inventory

### 1. LBP Conversion Analysis - Free to Premium Tracking
**Purpose**: Track conversion from free Lotto Bonus (bonus_type_id=32) to LBP premium purchases  
**Category**: Conversion Analysis / Performance Tracking  
**Business Metric**: Weekly conversion funnel from free experience to premium upgrade

```sql
select
    'LBP'                                           as product_name,
    a.week_start,
    a.cz_range,
    a.is_PU_30d,
    weekly_imp_events,
    weekly_imp_users,
    coalesce(weekly_trx, 0)                         as weekly_trx,
    coalesce(b.weekly_PUs, 0)                       as weekly_PUs,
    coalesce(b.weekly_gross_amount, 0)              as weekly_gross_amount,
    coalesce(b.weekly_net_amount, 0)                as weekly_net_amount,
    (coalesce(b.weekly_PUs, 0)) / weekly_imp_users  as weekly_cov_users,
    (coalesce(b.weekly_trx, 0)) / weekly_imp_events as weekly_cov_events

from (select
          date_trunc('week', bonus_date)::date                as week_start,
          coalesce(cz_range, '0-4.99')                        as cz_range,
          case when b.b_user_id is not null then 1 else 0 end as is_PU_30d,
          count(*)                                            as weekly_imp_events,
          count(distinct user_id)                             as weekly_imp_users
/*lotto bonus - free*/
      from (select distinct
                user_id,
                bonus_ts,
                bonus_date,
                reward_request_id
            from dwh.fact_sm_bonus_history
            where 1 = 1
              and user_id not in (select distinct user_id from dwh.playtika_users)
              and user_id not in
                  (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
              and bonus_type_id = 32
              and bonus_date >= '2026-02-01'::date) a
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
                         on a.user_id = c.c_user_id and a.bonus_date = c.event_date_datamining
      group by 1, 2, 3) a
/*LBP*/
         left join (select
                        date_trunc('week', tran_date)::date                 as week_start,
                        coalesce(cz_range, '0-4.99')                        as cz_range,
                        case when b.b_user_id is not null then 1 else 0 end as is_PU_30d,
                        count(distinct tran_id)                             as weekly_trx,
                        count(distinct user_id)                             as weekly_PUs,
                        sum(gross_amount)                                   as weekly_gross_amount,
                        sum(net_amount)                                     as weekly_net_amount

/*LBP- payments*/
                    from (SELECT
                              user_id,
                              tran_date,
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
                            and Product_Name ilike '%lbp%'
                            and tran_date >= '2026-02-01'::date) a
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
                                       on a.user_id = c.c_user_id and a.tran_date = c.event_date_datamining
                    group by 1, 2, 3) b
                   on a.week_start = b.week_start and a.cz_range = b.cz_range and a.is_PU_30d = b.is_PU_30d;
```

### 2. LBP Multiplier Validation - Freemium vs Premium Gatekeeping
**Purpose**: Validate reward calculation accuracy for both free and premium Lotto Bonus  
**Category**: Gatekeeping / Quality Assurance  
**Business Metric**: Mathematical validation of complex multiplier system integrity

```sql
/* Lotto Freemium / Premium Gate-keeping */

select
    sum(data_total_reward) / sum(calculated_total_reward) as ratio

from (select
          user_id,
          event_ts,
          tran_id,
          lotto_type,
          total_reward     as data_total_reward,
          level_multiplier * segment_multiplier * tier_multiplier * strong_ball_multiplier *
          ball_multipliers as calculated_total_reward

      from (select
                user_id,
                lotto_type,
                event_ts,
                tran_id,
                level_multiplier * 100                                                    as level_multiplier,
                (tier_multiplier + 1)                                                     as tier_multiplier,
                segment_multiplier,
                total_reward,
                coalesce(sum(case when ball_type = 'STRONG' then ball_multiplier end), 1) as strong_ball_multiplier,
                sum(case when ball_type = 'REGULAR' then ball_multiplier end)             as ball_multipliers

            from dwh.sm_fact_lotto_bonus lbp
                     left join dwh.dim_sm_bonus_type bt
                               on bt.bonus_type_id = lbp.bonus_type_id
            where true
              and event_ts >= '2025-03-19 12:00:00'
            --  and user_id = 154000066502254 /* May ID */
            --and tran_id is not null
            group by 1, 2, 3, 4, 5, 6, 7, 8) a) A;
```

### 3. LBP Ball Multiplier Analysis by Test Group & Lotto Type
**Purpose**: Analyze ball multiplier performance across A/B test groups and lotto types  
**Category**: A/B Testing / Performance Analysis  
**Business Metric**: Hourly multiplier distribution validation with median/average tracking

```sql
--- regular - 3 balls, AVG 8602, Median 2600
--- multi ball - 1 ball, AVG 15.86, Median 12

select
    event_ts::date                                                  as date,
    hour(event_ts)                                                  as hour,
    -- lotto_type,
    group_name,
    case when lotto_type = 'old' then 'freemium' else 'premium' end as lotto_type_new,
    avg(strong_ball_multiplier)                                     as AVG_strong_ball_multiplier,
    avg(ball_multipliers)                                           as AVG_ball_multipliers,
    max(MEDIAN_ball_multipliers)                                    as MEDIAN_ball_multipliers,
    max(MEDIAN_strong_ball_multiplier)                              as MEDIAN_strong_ball_multiplier,
    count(distinct user_id)                                         as trx
from (select *,
             median(strong_ball_multiplier)
             over ( partition by event_ts::date, hour(event_ts), lotto_type) as MEDIAN_strong_ball_multiplier,
             median(ball_multipliers)
             over ( partition by event_ts::date, hour(event_ts), lotto_type) as MEDIAN_ball_multipliers

      from (select
                lbp.user_id,
                case when group_name is null then 'control' else group_name end           as group_name,
                lotto_type,
                event_ts,
                tran_id,
                level_multiplier * 100                                                    as level_multiplier,
                (tier_multiplier + 1)                                                     as tier_multiplier,
                segment_multiplier,
                total_reward,
                coalesce(sum(case when ball_type = 'STRONG' then ball_multiplier end), 1) as strong_ball_multiplier,
                sum(case when ball_type = 'REGULAR' then ball_multiplier end)             as ball_multipliers

            from dwh.sm_fact_lotto_bonus lbp
                     left join dwh.dim_sm_bonus_type bt
                               on bt.bonus_type_id = lbp.bonus_type_id


                /*test groups*/
                     left join
                 (select
                      a.user_id,
                      group_name
                  from ((SELECT
                             a.user_id,
                             case
                                 WHEN group_name = 'Test_NoBucks'
                                     THEN 'Test medium BUCKS (original group)' end as group_name --first test
                         FROM sm_src_ds.src_sm_abtest_user_allocations A
                                  left join sm_ds.abtest_dim_test t
                                            on a.ab_test_id = t.ab_test_id
                                  left join sm_ds.abtest_dim_group g
                                            on a.test_group_id = g.test_group_id
                         where a.ab_test_id = 'E61vWaMYAu'
                           and group_name = 'Test_NoBucks')
                        union
                        (select
                             user_id,
                             'Test NO BUCKS second opening' as group_name --second test
                         from sm_draft.nobucks_allocation_2025_02_20
                         where group_name = 1)
                        union
--third test
                        (select
                             user_id,
                             case
                                 when a.group = 1 then 'Multipliers test - First Group'
                                 when a.group = 2 then 'Multipliers test - Second Group' end as groups
                         from sm_draft.final_allocation a
                         where a.group in (1, 2))) a) c
                 on lbp.user_id = c.user_id
            where true
              and event_ts >= '2025-03-19 12:00:00'
            --               and lbp.user_id not in (select distinct user_id from dwh.playtika_users)
--                 and lbp.user_id not in (select distinct user_id from dwh.sm_fact_journey_state_notifications where step_id = 539265)
            --    and user_id = 154000066502254 /* May ID */
            --and tran_id is not null
            group by 1, 2, 3, 4, 5, 6, 7, 8, 9) A) A
group by 1, 2, 3, 4
order by date, hour;
```

## Enhanced Technical Analysis & Business Intelligence

### **Core LBP Table Structure Revealed:**

#### **Primary Event Table**
- **`dwh.sm_fact_lotto_bonus`**: Central LBP events and multiplier tracking
  - **lotto_type**: 'old' (freemium) vs premium variants
  - **ball_type**: 'STRONG' vs 'REGULAR' ball mechanics  
  - **ball_multiplier**: Individual ball multiplier values
  - **total_reward**: Final calculated reward amount
  - **tran_id**: Links to premium purchase transactions when present

#### **Free Lotto Bonus Tracking**
- **`dwh.fact_sm_bonus_history`**: Free lotto bonus events
  - **bonus_type_id=32**: Free Lotto Bonus trigger events
  - **reward_request_id**: Session grouping for multiple events

#### **Complex Multiplier System**
- **Level Multiplier**: `level_multiplier * 100` (player level based)
- **Tier Multiplier**: `(tier_multiplier + 1)` (spending tier enhancement)  
- **Segment Multiplier**: User segment classification multiplier
- **Strong Ball Multiplier**: Special ball bonus (defaults to 1 if none)
- **Ball Multipliers**: Sum of regular ball multiplier values

### **A/B Testing Framework - Multiple Historical Tests:**

#### **Test 1 - Original No Bucks Test**
- **Test ID**: `E61vWaMYAu` 
- **Group**: `Test_NoBucks` → 'Test medium BUCKS (original group)'
- **Focus**: SlotoBucks integration testing

#### **Test 2 - Second No Bucks Opening**
- **Allocation Table**: `sm_draft.nobucks_allocation_2025_02_20`
- **Group**: 'Test NO BUCKS second opening'
- **Timeline**: February 2025 expansion

#### **Test 3 - Multipliers Test**  
- **Allocation Table**: `sm_draft.final_allocation`
- **Groups**: 'Multipliers test - First Group' / 'Multipliers test - Second Group'
- **Focus**: Ball multiplier optimization

### **Business Intelligence Patterns:**

#### **Conversion Funnel Analysis**
- **Free Experience**: bonus_type_id=32 events (impression tracking)
- **Premium Upgrade**: Product_Name ILIKE '%lbp%' purchases
- **Weekly Tracking**: Date truncated weekly aggregation with CZ/payer segmentation
- **Conversion Rates**: Both user-level and event-level conversion tracking

#### **Ball Multiplier Performance Benchmarks**
- **Regular Balls**: 3 balls, AVG 8602, Median 2600
- **Multi Ball (Strong)**: 1 ball, AVG 15.86, Median 12
- **Hourly Analysis**: Performance variation by hour of day
- **Freemium vs Premium**: 'old' lotto_type = freemium, others = premium

#### **Mathematical Validation Framework**
- **Reward Integrity**: `data_total_reward / calculated_total_reward` ratio validation
- **Complex Formula**: `level * segment * tier * strong_ball * regular_balls`
- **Quality Assurance**: Ensures reward calculation accuracy across all multiplier components

### **Key Business Rules Identified:**

#### **Product Classification**
- **LBP Purchases**: Product_Name ILIKE '%lbp%' pattern matching
- **Free Triggers**: bonus_type_id = 32 in fact_sm_bonus_history
- **Premium Events**: tran_id presence indicates premium upgrade

#### **User Quality Filters**
- **Standard Exclusions**: Playtika users + journey step 539265
- **Recent Payer Classification**: 30-day revenue > 0 flagging
- **CZ Segmentation**: 6-bucket spending classification (0-4.99 through 100+)

---
**Source**: User-provided comprehensive LBP analytics queries covering conversion funnel tracking, complex multiplier validation, and multi-test A/B framework analysis with detailed ball mechanics insights.