# Slotomania SQL Query Examples - Non-CTE Patterns

## Universal Query Best Practices

### Data Source Selection Standards
**CZ Data**: Always use `dwh.sm_user_profile_datamining_snapshot` instead of `stg.stg_smart_seg_sm_cz_price_cut_test`
- **Rationale**: Staging tables are optimized for parameter creation, not ongoing analytical work
- **Performance**: Datamining snapshot is lighter weight and more appropriate for gatekeeping/analysis
- **Consistency**: Aligns with other snapshot table usage patterns across queries

**Example**:
```sql
-- ✅ CORRECT: Use datamining snapshot for CZ data
left join (
    select user_id, cz_price_cut_test
    from dwh.sm_user_profile_datamining_snapshot
    where event_date_datamining = current_date
) cz on a.user_id = cz.user_id

-- ❌ AVOID: Heavy staging table for ongoing work  
left join (
    select user_id, cz_price_cut_test
    from stg.stg_smart_seg_sm_cz_price_cut_test
) cz on a.user_id = cz.user_id
```

### Date Logic for Configuration Tables
**Promo Date vs Execution Date**: Use event-based `promo_date` instead of `current_date` for configuration joins
- **Rationale**: Configuration tables store rules by promo_date periods, not execution dates
- **Accuracy**: Ensures correct parameter application based on when events actually occurred
- **Consistency**: Aligns with how parameter systems calculate and store configurations

**Example**:
```sql
-- ✅ CORRECT: Event-based date matching
select 
    user_id, event_ts, revenue,
    date(event_ts::timestamp AT TIME ZONE 'UTC' at time zone 'Asia/Jerusalem' - interval '13 hours') as promo_date
from dwh.sm_fact_rv_client_events
-- Join with config using event promo_date
left join sm_draft.config_table config 
    on user_segment = config.segment
    and event_promo_date >= config.config_promo_date_from 
    and event_promo_date < config.config_promo_date_to

-- ❌ AVOID: Execution-based date matching
left join sm_draft.config_table config
    on user_segment = config.segment  
    and current_date >= config.config_promo_date_from  -- Misaligns with config logic
```

### Query Structure Optimization
**Avoid Unnecessary Summary Sections**: Main query should provide sufficient validation without duplication
- **Focus**: Include only relevant data in SELECT statements
- **Efficiency**: Remove duplicate summary queries that repeat the same logic  
- **Clarity**: Use simple validation patterns ('ok'/'wrong') in main query
- **Maintenance**: Fewer sections = easier to maintain and debug

**Example**:
```sql
-- ✅ CORRECT: Single focused query with validation
select 
    user_id, event_date, revenue,
    case when revenue >= min_threshold then 'ok' else 'wrong' end as validation_status
from events_with_config
where relevant_filters_only

-- ❌ AVOID: Unnecessary summary duplication
-- Main query + separate summary query repeating the same validation logic
```

### Data Validation Before Query Writing
**CRITICAL**: Always check actual data values before writing queries with assumptions

**Process**:
1. **Check actual column values** before writing filter conditions
2. **Validate field names and content** against real data  
3. **Test query logic** with known data samples
4. **Avoid assumptions** about naming conventions or value formats

**Example**:
```sql
-- ❌ WRONG: Writing queries based on assumptions
where placement_trigger in ('back_to_lobby', 'ROOC', 'ROOG')  -- Assumed values

-- ✅ CORRECT: First check actual data, then write filters
select distinct placement_trigger from table limit 100;
-- Results show: 'RETURN_TO_LOBBY', 'RUN_OUT_OF_COINS', 'floating-cloud-lobby'
where placement_trigger in ('RETURN_TO_LOBBY', 'RUN_OUT_OF_COINS')  -- Real values
```

**Common Assumption Mistakes**:
- Field naming conventions (snake_case vs UPPER_CASE vs camelCase)
- Abbreviations vs full names (ROOC vs RUN_OUT_OF_COINS)
- Date formats and time zones
- NULL handling and edge cases

### Essential vs Unnecessary Joins
**Rule**: Only join tables that contribute directly to the requested analysis

**Essential Join Criteria**:
- **Columns are used** in SELECT, WHERE, or calculation logic
- **Data is required** for the specific validation or analysis requested
- **No alternative source** provides the same information more efficiently

**Remove Unnecessary Joins**:
```sql
-- ❌ WRONG: Joining table but not using any columns
left join dwh.sm_user_profile up on a.user_id = up.user_id
-- No up.* columns used in query

-- ✅ CORRECT: Only join when columns are actually needed
left join dwh.sm_user_profile up on a.user_id = up.user_id
where up.country_name = 'US'  -- Actually using the joined data
```

**Platform Context Value**:
```sql
-- ✅ USEFUL: Platform info helps debugging and analysis
left join (
    select user_id, session_id, platform_id
    from dwh.fact_sm_sessions_kafka
    where session_creation_date = current_date
    group by 1, 2, 3
) j on a.user_id = j.user_id and a.session_id = j.session_id
```

### Query Structure and Comments
**Section Comments**: Use brief, descriptive comments for major join sections
```sql
/*rv table- offers*/
/*datamining- DPU_60_90*/  
/*bonus table- actual coins amount*/
/*test groups*/
```

**Consistent Aliasing**: Use short but meaningful aliases throughout
- `a` for main table, `b` for user data, `bonus`, `pres`, `mult`, `tier`
- Keep aliases intuitive and consistent across similar queries

### Multi-Table Connection Chains for Game Mechanics
**CRITICAL**: Use proper relational keys instead of timing/session assumptions for connecting rewards

**Why Timing/Session Connections Are Unreliable**:
- **Multiple reward sources**: Users can receive same reward type from different sources (RV, purchases, daily bonuses, etc.)
- **Session overlap**: Multiple reward events can occur in same session
- **Timing variability**: Server processing delays can cause inconsistent timing between related events
- **Data race conditions**: Events may be logged out of order or with slight time differences

**Proper Connection Strategy**:
1. **Follow game mechanics flow** - trace through actual system tables (wheel, journey, etc.)
2. **Use relational keys** - `transaction_id`, `game_guid`, `parent_reward_request_id`
3. **Validate connection chain** - ensure each step uses proper foreign keys
4. **Test with known cases** - validate connection with specific user examples

**Example - RV Wheel Rewards Connection Chain**:
```sql
-- ✅ CORRECT: Follow proper relational chain
RV Event (transaction_id) → 
Bonus Journey (sku_id 200143) → 
Wheel Game (game_guid) → 
Goods/Rewards (parent_reward_request_id)

-- ❌ WRONG: Timing/session assumptions
-- Multiple hammer sources could exist in same session/timeframe
bonus_ts between event_ts and event_ts + interval '30 seconds'
-- OR: rv.session_id = bonus.session_id
```

**Investigation Approach**:
- Look for game-specific tables (`wheel`, `progressive`, `journey`, etc.)
- Identify proper connecting fields through schema analysis
- Trace one known example through the complete chain
- Document the connection pattern for reuse

### Template ID Usage in Offer Queries
**Important**: Template IDs are time-sensitive and offer-specific (see `context/business-knowledge/core-knowledge/business-context.md`)
- **Template IDs are provided by Ops team AFTER offers go live**
- **Previous template IDs may be outdated** for current analyses
- **Each template ID represents**: specific offer + specific segment + specific promo date + specific configuration
- **Usage**: Essential for gatekeeping and offer validation across all features (RV, Purchase Tools, Seasonals, Albums)

**Example**:
```sql
-- ✅ CURRENT: Use live template IDs from Ops team
where template_id = 221777  -- Current live offer ID

-- ⚠️ CAUTION: Previous template IDs may not apply to current period
where template_id = 123456  -- May be from previous promo period
```

## 1. User Balance Analysis with Percentiles

### Basic User Balance Distribution by Date
```sql
select distinct
    calc_date,
    percentile_cont(0.25) within group (order by balance_end_day)
    over (partition by calc_date) as p25_balance,
    percentile_cont(0.50) within group (order by balance_end_day)
    over (partition by calc_date) as median_balance,
    percentile_cont(0.75) within group (order by balance_end_day)
    over (partition by calc_date) as p75_balance,
    avg(balance_end_day) over (partition by calc_date) as avg_balance
from agg.agg_sm_daily_users_stats
where calc_date >= current_date - 30
and user_id not in (select distinct user_id from dwh.playtika_users)
and user_id in (
    select distinct user_id 
    from dwh.sm_fact_payments 
    where tran_status_id = 2 
    and artificial_ind = 0 
    and is_test = 0 
    and tran_date >= current_date - 60
);
```

### SlotoBucks Balance by CZ Ranges
```sql
select distinct
    calc_date,
    case
        when cz_price_cut_test >= 0 and cz_price_cut_test < 10 then '0-10'
        when cz_price_cut_test >= 10 and cz_price_cut_test < 50 then '10-50'
        when cz_price_cut_test >= 50 and cz_deluxe_weekly_update < 100 then '50-100'
        when cz_price_cut_test >= 100 then '100+'
    end as cz_ranges,
    percentile_cont(0.50) within group (order by sb_balance)
    over (partition by calc_date, case
        when cz_price_cut_test >= 0 and cz_price_cut_test < 10 then '0-10'
        when cz_price_cut_test >= 10 and cz_price_cut_test < 50 then '10-50'
        when cz_price_cut_test >= 50 and cz_price_cut_test < 100 then '50-100'
        when cz_price_cut_test >= 100 then '100+'
    end) as median_sb_balance,
    count(*) over (partition by calc_date, case
        when cz_price_cut_test >= 0 and cz_price_cut_test < 10 then '0-10'
        when cz_price_cut_test >= 10 and cz_price_cut_test < 50 then '10-50'
        when cz_price_cut_test >= 50 and cz_price_cut_test < 100 then '50-100'
        when cz_price_cut_test >= 100 then '100+'
    end) as user_count
from (
    select 
        a.calc_date,
        a.user_id,
        a.cz_price_cut_test,
        coalesce(sb.new_balance, 0) as sb_balance
    from agg.agg_sm_daily_users_stats a
    left join (
        select 
            user_id,
            date(timestamp) as calc_date,
            new_balance,
            row_number() over (
                partition by user_id, date(timestamp) 
                order by timestamp desc
            ) as rn
        from dwh.sm_fact_internal_purchase_balance_update_slotobucks
        where date(timestamp) >= current_date - 30
    ) sb on a.user_id = sb.user_id 
         and a.calc_date = sb.calc_date 
         and sb.rn = 1
    where a.calc_date >= current_date - 30
    and a.user_id not in (select distinct user_id from dwh.playtika_users)
) base_data;
```

## 2. Revenue and Payment Analysis

### Daily Revenue by Payment Type
```sql
select 
    tran_date,
    'Real Money' as payment_type,
    sum(gross_amount) as total_revenue,
    sum(net_amount) as net_revenue,
    count(distinct user_id) as unique_payers,
    count(distinct tran_id) as transaction_count
from dwh.sm_fact_payments
where tran_date >= current_date - 30
and tran_status_id = 2
and artificial_ind = 0
and is_test = 0
and user_id > 0
group by 1

union all

select 
    tran_date,
    'SlotoBucks' as payment_type,
    sum(gross_amount) as total_revenue,
    sum(net_amount) as net_revenue,
    count(distinct user_id) as unique_payers,
    count(distinct tran_id) as transaction_count
from dwh.sm_fact_virtual_payment_slotobucks
where tran_date >= current_date - 30
and tran_status_id = 2
and artificial_ind = 0
and is_test = 0
and user_id > 0
group by 1;
```

### Revenue by CZ Ranges and User Segments
```sql
select 
    tran_date,
    case
        when coalesce(cz_price_cut_test, 0) < 3 then '0-2.99'
        when cz_price_cut_test < 5 then '3-4.99'
        when cz_price_cut_test < 10 then '5-9.99'
        when cz_price_cut_test < 15 then '10-14.99'
        when cz_price_cut_test < 20 then '15-19.99'
        when cz_price_cut_test < 25 then '20-24.99'
        when cz_price_cut_test < 30 then '25-29.99'
        when cz_price_cut_test < 35 then '30-35.99'
        when cz_price_cut_test < 40 then '35-39.99'
        when cz_price_cut_test < 45 then '40-44.99'
        when cz_price_cut_test < 50 then '45-49.99'
        when cz_price_cut_test < 60 then '50-59.99'
        when cz_price_cut_test < 70 then '60-69.99'
        when cz_price_cut_test < 80 then '70-79.99'
        when cz_price_cut_test < 90 then '80-89.99'
        when cz_price_cut_test < 100 then '90-99.99'
        when cz_price_cut_test < 130 then '100-129.99'
        when cz_price_cut_test < 160 then '130-159.99'
        when cz_price_cut_test < 200 then '160-199.99'
        when cz_price_cut_test < 400 then '200-399.99'
        when cz_price_cut_test < 600 then '400-599.99'
        when  cz_price_cut_test < 10000 then '600-9999.99'
        end as cz_range,
    sum(net_amount) as net_revenue,
    count(distinct a.user_id) as unique_payers,
    avg(net_amount) as avg_transaction_value
from dwh.sm_fact_payments a
left join dwh.sm_user_profile_datamining_snapshot profile
    on a.user_id = profile.user_id 
    and a.tran_date = profile.event_date_datamining
where a.tran_date >= current_date - 30
and a.tran_status_id = 2
and a.artificial_ind = 0
and a.is_test = 0
and a.user_id > 0
and a.user_id not in (select distinct user_id from dwh.playtika_users)
group by 1, 2;
```

## 3. Game Activity and Spin Analysis

### Daily Spin Activity with Ante Bet Analysis
```sql
select 
    spin_date,
    count(distinct user_id) as active_spinners,
    sum(bet_amount) as total_bets,
    sum(win_amount) as total_wins,
    sum(win_amount) / sum(bet_amount) as overall_payout_ratio,
    sum(antebet_amounts_mega_pod) as mega_pod_antes,
    sum(antebet_amounts_scapes) as winovate_antes,
    sum(antebet_amounts_slotoquest) as sloto_quest_antes,
    sum(coalesce(royal_jackpot_antebet_amount, 0) + 
        coalesce(antebet_amounts_dynamic_jackpot, 0)) as jackpot_antes
from dwh.fact_sm_spin_history_kafka
where spin_date >= current_date - 30
and user_id not in (select distinct user_id from dwh.playtika_users)
and user_id not in (
    select distinct user_id 
    from dwh.sm_fact_journey_state_notifications 
    where step_id = 539265
)
group by 1
order by 1;
```

### Machine Performance Analysis
```sql
select 
    machine_data.machine_name,
    spin_date,
    count(distinct spin_data.user_id) as unique_players,
    sum(spin_data.bet_amount) as total_bets,
    sum(spin_data.win_amount) as total_wins,
    sum(spin_data.win_amount) / sum(spin_data.bet_amount) as payout_ratio,
    avg(spin_data.bet_amount) as avg_bet_size
from dwh.fact_sm_spin_history_kafka spin_data
left join dwh.sm_fact_machines_characteristics_data machine_data
    on spin_data.machine_type_id = machine_data.machine_id
where spin_date >= current_date - 7
and spin_data.user_id not in (select distinct user_id from dwh.playtika_users)
and spin_data.bet_amount > 0
group by 1, 2
having sum(spin_data.bet_amount) > 1000  -- Filter for meaningful volume
order by 2, 7 desc;
```

## 4. User Engagement and Churn Analysis

### Login Frequency and Engagement Patterns
```sql
select 
    calc_date,
    case 
        when days_since_last_login <= 1 then 'Daily Active'
        when days_since_last_login <= 7 then 'Weekly Active'
        when days_since_last_login <= 30 then 'Monthly Active'
        else 'Inactive'
    end as engagement_level,
    count(distinct user_id) as user_count,
    avg(daily_net_revenue) as avg_daily_revenue,
    sum(bet_coins) as total_coins_bet
from (
    select 
        current_stats.calc_date,
        current_stats.user_id,
        current_stats.daily_net_revenue,
        current_stats.bet_coins,
        coalesce(
            datediff('day', 
                max(previous_stats.calc_date), 
                current_stats.calc_date
            ), 999
        ) as days_since_last_login
    from agg.agg_sm_daily_users_stats current_stats
    left join agg.agg_sm_daily_users_stats previous_stats
        on current_stats.user_id = previous_stats.user_id
        and previous_stats.calc_date < current_stats.calc_date
        and previous_stats.calc_date >= current_stats.calc_date - 30
    where current_stats.calc_date >= current_date - 7
    and current_stats.user_id not in (select distinct user_id from dwh.playtika_users)
    group by 1, 2, 3, 4
) engagement_data
group by 1, 2
order by 1, 2;
```

### Tier Progression Analysis
```sql
select 
    calc_date,
    first_session_tier,
    last_session_tier,
    case 
        when last_session_tier > first_session_tier then 'Tier Up'
        when last_session_tier < first_session_tier then 'Tier Down'
        else 'Same Tier'
    end as tier_movement,
    count(distinct user_id) as user_count,
    avg(daily_net_revenue) as avg_revenue,
    avg(balance_end_day) as avg_end_balance
from agg.agg_sm_daily_users_stats
where calc_date >= current_date - 30
and first_session_tier is not null
and last_session_tier is not null
and user_id not in (select distinct user_id from dwh.playtika_users)
group by 1, 2, 3, 4
order by 1, 2, 3;
```

## 5. Virtual Currency Analysis

### SlotoBucks Flow Analysis
```sql
select 
    date(timestamp) as event_date,
    event_type,
    case when delta > 0 then 'Earned' else 'Spent' end as flow_direction,
    sum(abs(delta)) as total_amount,
    count(distinct user_id) as unique_users,
    count(*) as transaction_count,
    avg(abs(delta)) as avg_transaction_size
from dwh.sm_fact_internal_purchase_balance_update_slotobucks
where timestamp >= current_date - 30
and event_type <> 'initialBalance'
and user_id not in (select distinct user_id from dwh.playtika_users)
and user_id in (
    select distinct user_id 
    from dwh.sm_fact_payments 
    where tran_status_id = 2 
    and artificial_ind = 0 
    and is_test = 0 
    and tran_date >= current_date - 60
)
group by 1, 2, 3
order by 1, 2, 3;
```

### Gems Economy Analysis
```sql
select 
    calc_date,
    case when sku_name is not null then 'Gems Used' else 'Gems Received' end as transaction_type,
    coalesce(event_type, sku_name) as event_source,
    sum(case when delta > 0 then delta else 0 end) as gems_received,
    sum(case when delta < 0 then abs(delta) else 0 end) as gems_spent,
    sum(delta) as net_gems_change,
    count(distinct user_id) as unique_users
from (
    select 
        date(balance_update.timestamp) as calc_date,
        balance_update.user_id,
        balance_update.delta,
        balance_update.event_type,
        purchase_data.sku_name
    from dwh.sm_fact_internal_purchase_balance_update balance_update
    left join (
        select 
            purchase.purchase_id,
            purchase.user_id,
            purchase.timestamp,
            sku.sku_name
        from dwh.sm_fact_internal_purchases purchase
        left join dwh.dim_sku_type sku on purchase.sku_id = sku.sku_id
        where purchase.currency_id = 10000
        and purchase.timestamp::date >= current_date - 30
    ) purchase_data on balance_update.purchase_id = purchase_data.purchase_id
    where balance_update.timestamp::date >= current_date - 30
    and balance_update.user_id > 0
    and balance_update.currency_id = 10000
    and balance_update.user_id not in (select distinct user_id from dwh.playtika_users)
) gems_data
group by 1, 2, 3
order by 1, 2, 3;
```

## 6. Performance and Velocity Metrics

### Balance Velocity by Tier
```sql
select distinct
    calc_date,
    first_session_tier,
    percentile_cont(0.50) within group (order by velocity)
    over (partition by calc_date, first_session_tier) as median_velocity,
    avg(velocity) over (partition by calc_date, first_session_tier) as avg_velocity,
    count(*) over (partition by calc_date, first_session_tier) as user_count
from (
    select 
        calc_date,
        first_session_tier,
        user_id,
        case 
            when balance_start_day > 0 
            then (bet_coins - win_coins) / balance_start_day 
            else 0 
        end as velocity
    from agg.agg_sm_daily_users_stats
    where calc_date >= current_date - 30
    and first_session_tier >= 1
    and bet_coins > 0
    and balance_start_day > 1
    and user_id not in (select distinct user_id from dwh.playtika_users)
    and user_id in (
        select distinct user_id 
        from dwh.sm_fact_payments 
        where tran_status_id = 2 
        and artificial_ind = 0 
        and is_test = 0 
        and tran_date >= current_date - 60
    )
) velocity_data
where first_session_tier is not null;
```

## 7. Complex Aggregation Patterns

### Multi-Level User Segmentation
```sql
select 
    segment_data.calc_date,
    segment_data.user_segment,
    segment_data.cz_segment,
    segment_data.tier_segment,
    count(distinct segment_data.user_id) as user_count,
    sum(segment_data.daily_revenue) as total_revenue,
    avg(segment_data.daily_revenue) as avg_revenue_per_user,
    sum(segment_data.total_bets) as total_betting_volume
from (
    select 
        stats.calc_date,
        stats.user_id,
        stats.daily_net_revenue as daily_revenue,
        stats.bet_coins as total_bets,
        case 
            when stats.daily_net_revenue > 0 then 'Paying'
            else 'Non-Paying'
        end as user_segment,
        case
            when profile.cz_price_cut_test < 10 then 'Low CZ'
            when profile.cz_price_cut_test < 50 then 'Medium CZ'
            else 'High CZ'
        end as cz_segment,
        case
            when stats.last_session_tier < 5 then 'Low Tier'
            when stats.last_session_tier < 10 then 'Medium Tier'
            else 'High Tier'
        end as tier_segment
    from agg.agg_sm_daily_users_stats stats
    left join dwh.sm_user_profile_datamining_snapshot profile
        on stats.user_id = profile.user_id 
        and stats.calc_date = profile.event_date_datamining
    where stats.calc_date >= current_date - 7
    and stats.user_id not in (select distinct user_id from dwh.playtika_users)
    and stats.user_id > 0
) segment_data
group by 1, 2, 3, 4
order by 1, 2, 3, 4;
```

## Query Optimization Tips

### 1. **Filter Early and Often**
- Apply user exclusions in subqueries before joins
- Use date range filtering at the lowest level
- Filter on indexed columns first

### 2. **Efficient Window Functions**
- Use appropriate partitioning to reduce computation
- Combine multiple window functions with same partitioning
- Use DISTINCT when calculating percentiles on large datasets

### 3. **Strategic JOINs**
- Use LEFT JOIN when related data might not exist
- Join on multiple conditions for data accuracy
- Consider join order for performance

### 4. **Subquery Organization**
- Nest subqueries logically rather than using CTEs
- Use meaningful aliases for complex subqueries
- Pre-aggregate data in subqueries when possible

These patterns provide a solid foundation for building complex analytics queries while maintaining performance and readability without using CTEs. 