# Album - SQL Queries

**Note**: This file contains actual SQL queries extracted from the Funky Family Album dashboards for Album analysis and investigations.

## Query Inventory

### 1. Card Progression Analysis
**Purpose**: Comprehensive album card progression analysis with launch tracking
**Tables**: `dwh.sm_fact_shiny_challenge_progression`, `sm_draft.ariel_dim_albums_info`, `dwh.sm_fact_payments`
**Validation**: Track card collection patterns and completion rates across album launches

```sql
SELECT *
FROM (
select
    calc_date,
    weeks_from_launch,
    days_from_launch,
    a.album_id,
    a.album_name,
    user_card_count,
    count(distinct user_id) as users,
    max(collected_cards) as collected_cards,
    median(user_card_count) OVER (PARTITION BY calc_date,a.album_id,a.album_name) AS median_cards_per_user
from
    (
        select
            event_date              as calc_date,
            days_from_launch,
            weeks_from_launch,
            user_id,
            album_name,
            album_id,
            total_unique_collected  as user_card_count,
            collected_cards
        from
            dwh.sm_fact_shiny_challenge_progression a
            join (
                 select
                     *,
                     datediff('dd', launch_date, event_date) as days_from_launch,
                     floor(datediff('dd', launch_date, event_date) / 7) as weeks_from_launch
                 from
                     (
                     select
                         *
                     from
                         sm_draft.ariel_dim_albums_info b
                     where
                           Album_type <> 'Communal'
                       and use_date = '2025-04-20'
                     ORDER BY album_id DESC
                     LIMIT 5) x
                 ) b
                 on event_date between launch_date and end_date + interval '14 days'
                    and a.album_id = b.Shiny_album_id
        where
              event_date >= launch_date
          and event_date <= end_date + interval '14 days'
        ) a
group by
    1,2,3,4,5,6
) a
order by calc_date desc, album_id desc, user_card_count
```

### 2. Wheel of Sets (WoS) Activation Analysis
**Purpose**: Analyze Wheel of Sets activation patterns and wild card rewards
**Tables**: `dwh.sm_fact_collectibles_cards`, `dwh.sm_fact_mini_game_create`, `dwh.fact_sm_sessions_kafka`
**Validation**: Track WoS usage and wild card distribution by tier

```sql
select
    a.created_date,
    a.tier_id,
    wos_activations, 
    users_activated,
    users_won_wild,
    wilds_won
from
    (
        select
            created_date,
            tier_id,
            count(distinct crafting_id) as wos_activations,
            count(distinct a.user_id)   as users_activated
        from
            dwh.sm_fact_collectibles_cards a
        where
              operation_type = 'Remove'
          and trigger_type_id = 7
          and wheel_option_id = 3
          and created_date between current_date - 7 and current_date - 1
        group by
            1,2
        ) a
    left join
        (
            select
                date(timestamp)           as date,
                tier_id,
                count(*)                  as wilds_won,
                count(distinct a.user_id) as users_won_wild
            from
                dwh.sm_fact_mini_game_create a
                left join dwh.fact_sm_sessions_kafka b
                on a.session_id = b.session_id
            where
                  source_type = 'CRAFTING'
              and game_type = 'wild-card'
              and date(timestamp) between current_date - 7 and current_date - 1
            group by
                1, 2
            ) b
        on a.tier_id = b.tier_id and a.created_date = b.date
```

### 3. Album Revenue Analysis by Period
**Purpose**: Comprehensive album revenue analysis with user segmentation and progression tracking
**Tables**: `dwh.sm_fact_payments`, `sm_draft.ariel_dim_albums_info`, `dwh.sm_fact_shiny_challenge_progression`
**Validation**: Track revenue patterns across album periods with progression correlation

```sql
select
    launch_date,
    album_name,
    album_id,
    days_from_launch,
    weeks_from_launch,
    case
        when card_perc < 0.25 then '0-25%'
        when card_perc < 0.5 then '25-50%'  
        when card_perc < 0.75 then '50-75%'
        when card_perc < 1 then '75-99%'
        when card_perc = 1 then '100%'
        else 'Other'
    end as card_completion_bucket,
    revenue_bucket,
    count(distinct user_id) as users,
    sum(net_amount) as revenue
from (
    select
        a.*,
        b.launch_date,
        b.album_name,
        b.album_id,
        b.days_from_launch,
        b.weeks_from_launch,
        b.card_perc,
        case
            when net_amount = 0 then '0'
            when net_amount <= 5 then '0-5'
            when net_amount <= 20 then '5-20'
            when net_amount <= 50 then '20-50'
            when net_amount <= 100 then '50-100'
            else '100+'
        end as revenue_bucket
    from dwh.sm_fact_payments a
    join (
        select
            user_id,
            launch_date,
            album_name,
            album_id,
            days_from_launch,
            weeks_from_launch,
            max(total_unique_collected) / max(collected_cards) as card_perc
        from dwh.sm_fact_shiny_challenge_progression p
        join (
            select *,
                datediff('dd', launch_date, event_date) as days_from_launch,
                floor(datediff('dd', launch_date, event_date) / 7) as weeks_from_launch
            from sm_draft.ariel_dim_albums_info
            where Album_type <> 'Communal'
            order by album_id desc
            limit 3
        ) alb on p.album_id = alb.Shiny_album_id 
            and event_date between launch_date and end_date + interval '14 days'
        group by 1,2,3,4,5,6
    ) b on a.user_id = b.user_id
    where tran_status_id = 2
      and artificial_ind = 0
      and is_test = 0
      and user_id > 0
      and date(tran_ts) between b.launch_date and dateadd('day', 28, b.launch_date)
) final_data
group by 1,2,3,4,5,6,7
```

### 4. Shiny Challenge Progression Analysis
**Purpose**: Track user progression through Shiny challenges with completion timing
**Tables**: `dwh.sm_fact_shiny_challenge_progression`, `sm_draft.ariel_dim_albums_info`, `dwh.sm_fact_payments`
**Validation**: Monitor progression patterns and purchaser behavior

```sql
select
    datediff('dd', launch_date, first_finishing_point) as days_from_launch,
    first_finishing_point,
    album_name,
    a.album_id,
    case when b.user_id is not null then 1 else 0 end  as is_PU,
    count(distinct a.user_id)                          as users
from
    (
    select
        user_id,
        launch_date,
        total_unique_collected,
        album_name,
        b.album_id,
        num_of_shiny_cards,
        min(event_date) as first_finishing_point
    from
        dwh.sm_fact_shiny_challenge_progression a
        join (
             select
                 *
             from
                 sm_draft.ariel_dim_albums_info b
             where
                 Album_type <> 'Communal'
             ORDER BY album_id DESC
             LIMIT 5)                           b
             on
                 event_date between launch_date and end_date + interval '14 days' and a.album_id=b.Shiny_album_id
    group by 1, 2, 3, 4, 5, 6) a
    left join (
              select distinct
                  user_id,
                  album_id
              from
                  dwh.sm_fact_payments
                  join (
                       select
                           *
                       from
                           sm_draft.ariel_dim_albums_info b
                       where
                           Album_type <> 'Communal'
                       ORDER BY album_id DESC
                       LIMIT 5)B
                       on
                           date(tran_ts) between launch_date and end_date
              where
                    user_id > 0
                and tran_status_id = 2
                and artificial_ind = 0
                and is_test = 0
              )                b
              on a.user_id = b.user_id and a.album_id = b.album_id
where
    total_unique_collected = num_of_shiny_cards
group by
    1, 2, 3, 4, 5
```

### 5. Shiny Show Floor Activity Analysis
**Purpose**: Analyze Shiny Show floor activity patterns by album period
**Tables**: `dwh.sm_fact_shiny_show`, `sm_draft.ariel_dim_albums_info`
**Validation**: Track Shiny Show engagement across different floor types

```sql
select
    album_id,
    event_date,
    floor_number,
    sum(shiny_acts)
from (select
          user_id,
          album_id,
          event_date,
          floor_number,
          COUNT(DISTINCT game_uid) as shiny_acts
      from dwh.sm_fact_shiny_show s
      join (select *
                     from sm_draft.ariel_dim_albums_info
                     where true
                     order by launch_date desc
                     limit 2
                    )             x on s.event_ts::date between launch_date and end_date - 1
      where true
        --   and user_id = 250
        --      and event_date >= current_date - 14
        and floor_type ilike '%shiny%'
      group by 1, 2, 3, 4
     ) a
group by 1, 2, 3
```

### 6. Album Card Acquisition Analysis
**Purpose**: Analyze card acquisition patterns including card sources and timing
**Tables**: `dwh.sm_fact_collectibles_cards`, `sm_draft.ariel_dim_albums_info`
**Validation**: Track how users acquire cards across different album periods

```sql
select
    album_id,
    album_name,
    launch_date,
    source_type,
    operation_type,
    days_from_launch,
    count(*) as card_operations,
    count(distinct user_id) as users
from (
    select
        c.*,
        a.album_id,
        a.album_name,
        a.launch_date,
        datediff('dd', a.launch_date, c.created_date) as days_from_launch
    from dwh.sm_fact_collectibles_cards c
    join (
        select *
        from sm_draft.ariel_dim_albums_info
        where Album_type <> 'Communal'
        order by album_id desc
        limit 3
    ) a on c.created_date between a.launch_date and a.end_date + interval '14 days'
    where c.created_date >= a.launch_date
) final_data
where source_type is not null
  and operation_type in ('Add', 'Remove')
group by 1,2,3,4,5,6
order by album_id desc, days_from_launch, source_type
```

### 7. Fusion Set Revenue Progression Analysis
**Purpose**: Comprehensive fusion set revenue analysis with time-based progression tracking
**Tables**: `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`, `sm_draft.ariel_dim_albums_info`
**Validation**: Monitor fusion set purchase patterns and revenue progression

```sql
select
    fusion_album_id,
    fusion_album_name,
    days_from_launch,
    weeks_from_launch,
    tier_bucket,
    revenue_bucket,
    count(distinct user_id) as users,
    sum(net_amount) as total_revenue,
    avg(net_amount) as avg_revenue_per_user
from (
    select
        p.*,
        a.fusion_album_id,
        a.fusion_album_name,
        a.launch_date,
        datediff('dd', a.launch_date, date(p.tran_ts)) as days_from_launch,
        floor(datediff('dd', a.launch_date, date(p.tran_ts)) / 7) as weeks_from_launch,
        case
            when p.decorated_tier_id <= 5 then '0-5'
            when p.decorated_tier_id <= 10 then '6-10'
            when p.decorated_tier_id <= 20 then '11-20'
            else '20+'
        end as tier_bucket,
        case
            when p.net_amount <= 1 then '0-1'
            when p.net_amount <= 5 then '1-5'
            when p.net_amount <= 20 then '5-20'
            when p.net_amount <= 50 then '20-50'
            else '50+'
        end as revenue_bucket
    from dwh.sm_fact_payments p
    join sm_draft.SM_DIM_Products pr on p.sku_id = pr.sku_id and p.transaction_source_type_id = pr.transaction_source_type_id
    join (
        select *
        from sm_draft.ariel_dim_albums_info
        where Album_type = 'Fusion'
        order by launch_date desc
        limit 3
    ) a on date(p.tran_ts) between a.launch_date and a.end_date + interval '14 days'
    where p.tran_status_id = 2
      and p.artificial_ind = 0
      and p.is_test = 0
      and p.user_id > 0
      and pr.Product_Name ilike '%fusion%'
) final_fusion_data
group by 1,2,3,4,5,6
order by fusion_album_id desc, days_from_launch, tier_bucket
```

### 8. Album Purchase Behavior Analysis
**Purpose**: Analyze purchase behavior patterns across different album types and periods
**Tables**: `dwh.sm_fact_payments`, `sm_draft.SM_DIM_Products`, `sm_draft.ariel_dim_albums_info`
**Validation**: Track purchase patterns and user behavior across album lifecycle

```sql
select
    album_type,
    album_name,
    product_category,
    days_from_launch_bucket,
    user_tier_bucket,
    count(distinct user_id) as purchasers,
    count(*) as transactions,
    sum(net_amount) as revenue,
    avg(net_amount) as avg_transaction_value
from (
    select
        p.*,
        a.album_type,
        a.album_name,
        case
            when pr.Product_Name ilike '%pack%' then 'Card Pack'
            when pr.Product_Name ilike '%wild%' then 'Wild Card'
            when pr.Product_Name ilike '%fusion%' then 'Fusion'
            when pr.Product_Name ilike '%boost%' then 'Booster'
            else 'Other'
        end as product_category,
        case
            when datediff('dd', a.launch_date, date(p.tran_ts)) <= 3 then '0-3 days'
            when datediff('dd', a.launch_date, date(p.tran_ts)) <= 7 then '4-7 days'
            when datediff('dd', a.launch_date, date(p.tran_ts)) <= 14 then '8-14 days'
            when datediff('dd', a.launch_date, date(p.tran_ts)) <= 28 then '15-28 days'
            else '28+ days'
        end as days_from_launch_bucket,
        case
            when p.decorated_tier_id <= 5 then 'Tier 0-5'
            when p.decorated_tier_id <= 15 then 'Tier 6-15'
            when p.decorated_tier_id <= 25 then 'Tier 16-25'
            else 'Tier 25+'
        end as user_tier_bucket
    from dwh.sm_fact_payments p
    join sm_draft.SM_DIM_Products pr on p.sku_id = pr.sku_id and p.transaction_source_type_id = pr.transaction_source_type_id
    join (
        select *
        from sm_draft.ariel_dim_albums_info
        order by launch_date desc
        limit 5
    ) a on date(p.tran_ts) between a.launch_date and a.end_date + interval '14 days'
    where p.tran_status_id = 2
      and p.artificial_ind = 0
      and p.is_test = 0
      and p.user_id > 0
      and (pr.Product_Name ilike '%album%' or pr.Product_Name ilike '%card%' or pr.Product_Name ilike '%wild%' or pr.Product_Name ilike '%fusion%')
) purchase_analysis
group by 1,2,3,4,5
order by album_type, album_name, days_from_launch_bucket, user_tier_bucket
```

---

**Related Files:**
- `queries-explanation.md` - Business logic, patterns, and query intelligence
- `general-album.md` - Complete Album business context