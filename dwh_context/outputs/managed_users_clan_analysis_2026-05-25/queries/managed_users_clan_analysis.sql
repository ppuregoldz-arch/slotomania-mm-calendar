/*
MANAGED USERS CLAN ANALYSIS QUERY
=================================

Query Purpose: Extract managed users with clan membership status and weak clan identification
Created: 2026-05-25
Requirements:
- Only managed users (have account manager)
- Tier 5+ users only
- Active in past 4 days
- Include clan membership and clan size information
- Identify weak clans (3+ users inactive for 10+ days)

VALIDATION DOCUMENTATION
========================
Validation Performed: Yes
Validation Entities: user_id 174, user_id 250, user_id 297
Validation Date Range: Current date - 4 days for activity, current date - 10 days for weak clan calculation
Raw Data Source: agg.agg_sm_daily_users_stats for activity, dwh.sm_clan_user_profile for clan membership
Expected Result: user 174: managed=1, clan_member=1, weak_clan=1; user 250: similar pattern
Actual Query Result: user 174: account_manager=Nitzan Shaked, is_clan_member=1, weak_clan=1
Validation Status: Passed
Notes: Query correctly identifies managed users with tier 5+, recent activity, and clan status
*/

select
    managed_users.user_id,
    managed_users.account_manager,
    case when clan_profile.clan_id is not null then 1 else 0 end as is_clan_member,
    coalesce(clan_size.num_of_clan_members, 0) as num_of_clan_members,
    case when weak_clans.clan_id is not null then 1 else 0 end as is_weak_clan
from (
    /*managed users - tier 5+ and active in past 4 days*/
    select distinct
        vip.user_id,
        vip.account_manager
    from dwh.sm_dim_vip_account_managers vip
    join dwh.sm_user_profile_snapshot ups
        on vip.user_id = ups.user_id
    join agg.agg_sm_daily_users_stats ds
        on vip.user_id = ds.user_id
        and ds.calc_date >= current_date - interval '4 days'
    where 1 = 1
        and vip.account_manager is not null
        and ups.tier_id >= 5
) managed_users
left join dwh.sm_clan_user_profile clan_profile
    on managed_users.user_id = clan_profile.user_id
left join (
    /*clan size calculation*/
    select
        clan_id,
        count(distinct user_id) as num_of_clan_members
    from dwh.sm_clan_user_profile
    group by 1
) clan_size
    on clan_profile.clan_id = clan_size.clan_id
left join (
    /*weak clans - clans with 3+ users inactive for 10+ days*/
    select distinct clan_id
    from (
        select
            cp.clan_id,
            count(distinct case when ds_recent.user_id is null then cp.user_id end) as inactive_users_count
        from dwh.sm_clan_user_profile cp
        left join (
            select distinct user_id
            from agg.agg_sm_daily_users_stats
            where calc_date >= current_date - interval '10 days'
        ) ds_recent
            on cp.user_id = ds_recent.user_id
        group by 1
    ) clan_activity
    where inactive_users_count >= 3
) weak_clans
    on clan_profile.clan_id = weak_clans.clan_id
order by 1;