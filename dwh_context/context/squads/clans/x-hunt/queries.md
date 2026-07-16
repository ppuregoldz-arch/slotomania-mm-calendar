# X-Hunt - SQL Queries

**Note**: This file contains actual SQL queries provided by the user for X-Hunt analysis and investigations.

## Related Documentation Files
- `queries-explanation.md` - Query intelligence and business logic extraction
- `business-context.md` - X-Hunt business context
- `general-x-hunt.md` - Complete X-Hunt feature overview

---

## 1. X-Hunt Progression Analysis

**Purpose**: Track X-Hunt progression metrics with revenue share analysis for active chase participants  
**Tables**: `dwh.sm_fact_xhunt_progress_event`, `agg.agg_sm_daily_promotion_stats`, `dwh.dim_dates`  
**Parameters**: `Parameter 1` (start date), `Parameter 2` (chase_id)  
**Validation**: Monitor user progression through chase steps with 14-day rolling revenue contribution

```sql
-- PROGRESSION Query from Clan Xhunt 06.05 (7).twbx
-- Datasource Caption: "progrssion- rev share and users share- only active users, rolling rev"

select 
    date as promo_date,
    filled_current_steps as current_step,
    max(DAU) as DAU,
    count(distinct user_id) as users,
    count(distinct user_id) / max(DAU) as user_share,
    sum(rs_14d) as rs_14d,
    max(overall_PU_14d) as overall_PU_14d,
    count(distinct is_PU_14d) as PUs_14_days,
    count(distinct is_PU_14d)/max(overall_PU_14d) as PUs_share
from (
    select
        a.*,
        b.*,
        c.DAU,
        e.overall_PU_14d,
        case when c.user_id is not null then 1 else 0 end as is_daily_active,
        c.is_PU_14d,
        c.rs_14d,
        last_value(current_steps ignore nulls) over (
            partition by b.user_id
            order by date
        ) as filled_current_steps
    /*dates*/
    from (
        select date
        from dwh.dim_dates
        where 1 = 1
          and date >= [Parameters].[Parameter 1]::date
          and date < [Parameters].[Parameter 1]::date+20
    ) a
    /*distinct users- chase*/
    cross join (
        select distinct user_id
        from dwh.sm_fact_xhunt_progress_event
        where 1 = 1
          and chase_id = [Parameters].[Parameter 2]
          and event_date >= [Parameters].[Parameter 1]::date
        --  and user_id in (2063461, 151325304769604, 5873146)
    ) b
    /*rs - 14 days back, active users*/
    left join (
        select *,
            user_rev_14d / overall_rev_14d as rs_14d,
            case when user_rev_14d > 0 then user_id else null end as is_PU_14d
        from (
            select
                user_id,
                promo_date,
                gross_rev,
                sum(gross_rev) over (
                    partition by user_id 
                    order by promo_date 
                    rows between 13 preceding and current row
                ) as user_rev_14d,
                sum(gross_rev) over (
                    order by promo_date 
                    rows between 13 preceding and current row
                ) as overall_rev_14d
            from agg.agg_sm_daily_promotion_stats
            where 1 = 1
              and promo_date >= [Parameters].[Parameter 1]::date - 14
              and promo_date < current_date
        ) rev_calc
        where user_rev_14d > 0  -- only paying users
    ) c on a.date = c.promo_date and b.user_id = c.user_id
    /*DAU*/
    left join (
        select 
            promo_date,
            count(distinct user_id) as DAU
        from agg.agg_sm_daily_promotion_stats
        where 1 = 1
          and promo_date >= [Parameters].[Parameter 1]::date - 14
        group by 1
    ) d on a.date = d.promo_date
    /*overall PU count - 14 days*/
    left join (
        select 
            promo_date,
            count(distinct user_id) as overall_PU_14d
        from agg.agg_sm_daily_promotion_stats
        where gross_rev > 0
          and promo_date >= [Parameters].[Parameter 1]::date - 14
        group by 1
    ) e on a.date = e.promo_date
) base_data
where filled_current_steps is not null  -- only users with chase progress
group by 1, 2
order by 1, 2;
```

---

## 2. X-Hunt Simulation Analysis (Clan Context)

**Purpose**: Simulate X-Hunt progression for all clan users to model potential engagement and revenue impact  
**Tables**: `dwh.sm_clan_user_profile`, `agg.agg_sm_daily_promotion_stats`, `dwh.dim_dates`  
**Context**: What-if analysis for clan-wide X-Hunt participation  
**Validation**: Model revenue and participation patterns for strategic planning

```sql
-- SIMULATION Query from Clan Xhunt 06.05 (7).twbx
-- Datasource Caption: "Simulation - progression"

select 
    promo_date,
    calculated_current_step,
    max(DAU)                                        as DAU,
    count(distinct user_id)                         as users,
    count(distinct user_id) / max(DAU)              as user_share,
    sum(rs_14d)                                     as rs_14d,
    max(overall_PU_14d)                             as overall_PU_14d,
    count(distinct is_PU_14d)                       as PUs_14_days,
    count(distinct is_PU_14d) / max(overall_PU_14d) as PUs_share
from (
    select
        a.*,
        b.*,
        c.DAU,
        e.overall_PU_14d,
        case when c.user_id is not null then 1 else 0 end as is_daily_active,
        c.is_PU_14d,
        c.rs_14d,
        last_value(calculated_current_steps ignore nulls) over (
            partition by b.user_id
            order by date
        ) as filled_current_steps
    /*dates*/
    from (
        select date
        from dwh.dim_dates
        where 1 = 1
          and date >= '2026-05-06'::date - 17
          and date < '2026-05-06'::date
    ) a
    /*distinct users- users who have a clan*/
    cross join (
        select distinct user_id
        from dwh.sm_clan_user_profile
        where 1 = 1
    ) b
    /*rs - 14 days back, active users*/
    left join (
        select *,
            user_rev_14d / overall_rev_14d                        as rs_14d,
            case when user_rev_14d > 0 then user_id else null end as is_PU_14d
        from (
            select
                user_id,
                promo_date,
                gross_rev,
                sum(gross_rev) over (
                    partition by user_id 
                    order by promo_date 
                    rows between 13 preceding and current row
                ) as user_rev_14d,
                sum(gross_rev) over (
                    order by promo_date 
                    rows between 13 preceding and current row
                ) as overall_rev_14d
            from agg.agg_sm_daily_promotion_stats
            where 1 = 1
              and promo_date >= '2026-05-06'::date - 31
              and promo_date < current_date
        ) rev_calc
    ) c on a.date = c.promo_date and b.user_id = c.user_id
    /*DAU*/
    left join (
        select 
            promo_date,
            count(distinct user_id) as DAU
        from agg.agg_sm_daily_promotion_stats
        where 1 = 1
          and promo_date >= '2026-05-06'::date - 31
        group by 1
    ) d on a.date = d.promo_date
    /*overall PU count*/
    left join (
        select 
            promo_date,
            count(distinct user_id) as overall_PU_14d
        from agg.agg_sm_daily_promotion_stats
        where gross_rev > 0
          and promo_date >= '2026-05-06'::date - 31
        group by 1
    ) e on a.date = e.promo_date
) base_data
group by 1, 2
order by 1, 2;
```