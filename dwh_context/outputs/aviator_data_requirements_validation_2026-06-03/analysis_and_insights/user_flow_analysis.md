# Aviator User Flow - Event Tracking Analysis

## Overview

This analysis maps the Aviator user experience to the implemented event structure, showing how player actions translate to data collection points for comprehensive analytical coverage.

---

## User Journey Flow Diagram

```
PURCHASE DECISION
       ↓
   [PAID PATH]                    [BONUS PATH]
       ↓                              ↓
QUALIFYING PURCHASE            BONUS TRIGGER
       ↓                              ↓
   📊 Event 1: FROZEN         📊 Event 1: FROZEN
   (Config Locked)            (Config Locked)  
       ↓                              ↓
   📊 Event 2: READY_TO_PLAY  📊 Event 2: READY_TO_PLAY
   (After payment callback)    (Same timestamp as Event 1)
       ↓                              ↓
       └──────────────┬───────────────┘
                      ↓
              [OFFER INTERACTION]
                      ↓
               USER DECISION
                   ↙     ↘
          DECLINE OFFER   PROCEED TO GAME
               ↓               ↓
    📊 Event 3: OFFER_DECLINED  GAME ENTRY
           (End Flow)           ↓
                        [ROUND 1 START]
                               ↓
                    📊 Event 4: ROUND_STARTED
                               ↓
                        [PLAYER GAMEPLAY]
                      ↙              ↘
              PLAYER LOCKS        TIMEOUT/CRASH
                    ↓                   ↓
            📊 Event 5: ROUND_ENDED (LOCK)  📊 Event 5: ROUND_ENDED (CRASH)
                    ↓                   ↓
                    └───────┬───────────┘
                            ↓
                     [MORE ROUNDS?]
                        ↙         ↘
                    YES             NO
                     ↓               ↓
              [ROUND N START]   [FINAL REWARD]
                     ↓               ↓
           📊 Event 4: ROUND_STARTED  📊 Event 6: USER_REWARDED
                     ↓               (Coins delivered)
              [Continue Loop]
```

---

## Event-by-Event User Flow Analysis

### Event 1: FROZEN - Configuration Lock
**User Experience**: Invisible to user - happens at purchase callback
**Business Logic**: System locks in player's segment configuration and round parameters

```
Trigger: Qualifying purchase completed OR bonus game triggered
User State: Unaware - background process
Data Captured:
├── User Context (user_id, session_id, segment_id)  
├── Game Setup (game_id, config_id, base_amount)
├── Entry Path (PAID vs BONUS)
├── Configuration Snapshot (growth_formula, total_rounds)
└── BOGO Chain Data (bonus_game_sequence_idx, parent_game_id)
```

**Analytical Value**: 
- Track configuration effectiveness by segment
- Measure PAID vs BONUS entry distribution
- Analyze BOGO chain progression

### Event 2: READY_TO_PLAY - Game Available  
**User Experience**: Game becomes available in UI
**Business Logic**: For PAID - after payment processing; For BONUS - immediate

```
Trigger: Payment confirmed (PAID) OR immediate (BONUS)
User State: Sees Aviator option available
Data Captured:
├── Same base fields as Event 1
├── Transition timing (event_ts difference shows payment processing time)
└── Game availability confirmation
```

**Analytical Value**:
- Measure payment-to-availability lag for PAID path
- Track when games become available vs when players start them
- Identify drop-off between availability and gameplay initiation

### Event 3: OFFER_DECLINED - Paid Offer Rejection
**User Experience**: Player explicitly declines paid Aviator offer
**Business Logic**: User chooses not to proceed with paid game option

```
Trigger: User clicks "Decline" on paid offer REST endpoint
User State: Explicitly rejects paid game opportunity  
Data Captured:
├── User Context (user_id, session_id)
├── Game Context (game_id, segment_id)
└── Declination timing (event_ts)
```

**Analytical Value**:
- Measure paid offer conversion rates
- Identify segments with high decline rates
- Optimize offer presentation and pricing

### Event 4: ROUND_STARTED - Round Initiation
**User Experience**: Player starts a round, sees multiplier begin growing
**Business Logic**: Round enters IN_PROGRESS state, crash point determined

```
Trigger: Player starts round (manual for PAID, auto for BONUS)
User State: Actively watching multiplier grow, deciding when to lock
Data Captured:
├── Round Context (round_idx, total_rounds)
├── Configuration Data (growth_formula snapshot)  
├── Timing Data (event_ts = round start time)
└── All base game context
```

**Analytical Value**:
- Track round initiation rates after game availability  
- Measure time-to-start for different user segments
- Analyze round progression patterns (which rounds get played)

### Event 5: ROUND_ENDED - Round Completion
**User Experience**: Player either locked in a multiplier or timed out/crashed
**Business Logic**: Round transitions to LOCKED or CRASHED state

```
Trigger: Player locks multiplier OR timeout/crash occurs
User State: Sees final round result, knows if more rounds available
Data Captured:
├── Outcome Details (end_round_reason: LOCK/CRASH, history_reason: detailed)
├── Performance Metrics (multiplier, duration_ms)
├── Final Game Result (ONLY on last round - game_result block)
└── Round completion context
```

**Special Case - Final Round**: Includes complete game summary:
- `game_result.coins` - Final reward calculation
- `game_result.winning_round_idx` - Which round achieved best multiplier  
- `game_result.winning_raw_multiplier` - Best multiplier achieved
- `game_result.bundle_ids` - Milestone rewards earned
- `game_result.applied_on_top_multiplier` - Promotional bonuses

**Analytical Value**:
- Measure player timing behavior (lock vs crash rates)
- Track multiplier achievement distribution  
- Analyze multi-round strategy evolution
- Measure promotional impact on outcomes

### Event 6: USER_REWARDED - Final Reward Delivery
**User Experience**: Player receives final coins/rewards in their account
**Business Logic**: Actual reward delivery to player account, cleanup of game state

```
Trigger: Player claims/collects final reward
User State: Reward received, game session complete
Data Captured:
├── Delivered Rewards (game_result.coins - actual delivered amount)
├── All game context for final reconciliation
└── Session completion timestamp
```

**Analytical Value**:
- Verify reward delivery vs calculation (Event 5 vs Event 6 comparison)
- Track collection rates and timing
- Final session success measurement

---

## Multi-Round Flow Patterns

### Standard 2-Round Game Flow
```
Round 1: Event 4 → Event 5 (outcome recorded, no game_result)
         ↓
Round 2: Event 4 → Event 5 (outcome + game_result with final summary)  
         ↓
Final:   Event 6 (reward delivery)
```

### BOGO Chain Flow (3+ Games)
```
Main Game:   Events 1,2,4,5,4,5,6 (parent_game_id = null)
             ↓
Bonus Game:  Events 1,2,4,5,4,5,6 (parent_game_id = main game_id)
             ↓  
Bonus Game:  Events 1,2,4,5,4,5,6 (parent_game_id = main game_id)
```

### Early Decline Flow
```
Purchase → Event 1: FROZEN → Event 2: READY_TO_PLAY → Event 3: OFFER_DECLINED
(End - no gameplay events)
```

---

## Player Behavior Analysis Opportunities

### 1. Conversion Funnel Analysis
```
Purchase Intent → Configuration Lock → Game Available → Game Started → Round Completion → Reward Collection

Tracking Points:
├── Event 1 Count = Total game configurations
├── Event 4 Count = Actual game starts  
├── Event 5 Count = Round completions
└── Event 6 Count = Final reward collections

Drop-off Analysis:
├── Event 1 → Event 4: Game availability to gameplay initiation
├── Event 4 → Event 5: Round start to completion  
├── Event 5 → Event 6: Game completion to reward collection
```

### 2. Player Timing Strategy Analysis
```
Lock Timing Patterns:
├── duration_ms distribution by user segment
├── Lock vs Crash rates by round number
├── Learning curve analysis (round 1 vs round 2 behavior)
└── Risk tolerance measurement (early lock vs timeout patterns)
```

### 3. Configuration Effectiveness Measurement
```
Economic Performance by Config:
├── config_id + segment_id combination performance
├── growth_formula parameter impact on player behavior
├── base_amount vs final_reward ratios by segment
└── total_rounds utilization rates
```

### 4. Promotional Impact Analysis
```
Promo Effectiveness:
├── applied_on_top_multiplier impact on engagement
├── bundle_ids achievement rates
├── BOGO chain completion patterns
└── Entry path (PAID vs BONUS) performance comparison
```

---

## Data Quality Validation Points

### Event Sequence Validation
```sql
-- Validate proper event sequences per game_id
-- Expected: 1,2,4,5,4,5,6 (2-round game)
-- Or: 1,2,3 (declined offer)

WITH event_sequences AS (
  SELECT game_id, 
         LISTAGG(event_type, ',') WITHIN GROUP (ORDER BY event_ts) as sequence
  FROM aviator_events 
  GROUP BY game_id
)
SELECT sequence, COUNT(*) as game_count
FROM event_sequences
GROUP BY sequence
ORDER BY game_count DESC;
```

### Round Progression Validation  
```sql
-- Ensure rounds progress logically (0,1,2... within game_id)
SELECT game_id, 
       COUNT(DISTINCT round_idx) as unique_rounds,
       MAX(round_idx) + 1 as expected_rounds,
       total_rounds
FROM aviator_events 
WHERE event_type IN ('ROUND_STARTED', 'ROUND_ENDED')
GROUP BY game_id, total_rounds
HAVING unique_rounds != expected_rounds;
```

### Timing Logic Validation
```sql
-- Validate event timing makes sense
SELECT game_id,
       MIN(CASE WHEN event_type = 'FROZEN' THEN event_ts END) as frozen_ts,
       MIN(CASE WHEN event_type = 'READY_TO_PLAY' THEN event_ts END) as ready_ts,
       MIN(CASE WHEN event_type = 'ROUND_STARTED' THEN event_ts END) as first_round_ts
FROM aviator_events
GROUP BY game_id
HAVING ready_ts < frozen_ts OR first_round_ts < ready_ts;
```

---

## Key Performance Indicators by Flow Stage

### Entry Metrics
- **Configuration Rate**: Event 1 count per day/segment
- **Availability Lag**: Event 2 timestamp - Event 1 timestamp (PAID path)
- **Offer Conversion**: (Event 4 count) / (Event 1 count - Event 3 count)

### Engagement Metrics  
- **Round Completion Rate**: Event 5 count / Event 4 count
- **Multi-Round Engagement**: Games with max(round_idx) > 0
- **Average Rounds Played**: AVG(max(round_idx) + 1) per game_id

### Outcome Metrics
- **Lock Success Rate**: Event 5 with end_round_reason = 'LOCK' / Total Event 5
- **Average Win Multiplier**: AVG(winning_raw_multiplier) from Event 6
- **Collection Rate**: Event 6 count / Event 5 count (final rounds)

### Business Metrics
- **Revenue per Game**: AVG(final_reward - base_amount)  
- **Player Value**: final_reward / base_amount ratio analysis
- **Segment Performance**: All metrics segmented by segment_id + config_id

---

## Conclusion

The 6-event structure provides comprehensive coverage of the Aviator user journey, enabling detailed funnel analysis, behavioral measurement, and business performance tracking. The event design supports both real-time monitoring and historical analysis of player engagement patterns, configuration effectiveness, and feature success metrics.

**Key Analytical Strengths**:
✅ Complete user journey coverage from purchase to reward  
✅ Detailed round-by-round player behavior tracking
✅ Configuration and promotional effectiveness measurement  
✅ Robust validation points for data quality assurance
✅ Multi-path support (PAID vs BONUS, BOGO chains)