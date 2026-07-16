# AVIATOR - Business Context

**Feature**: AVIATOR (Multiplier-Based Mini-Game)
**Purpose**: Time-dependent multiplier growth system with player claim timing strategy
**Source**: [Aviator Economy Requirements Wiki](https://wiki.playtika.com/spaces/SLOT/pages/983302503/Aviator+-+Economy+requirements)

## Feature Overview

Aviator is a **multiplier-based mini-game** where players must decide when to "cash out" before the multiplier crashes. The system combines time-dependent growth, strategic decision-making, and configurable economy parameters to create an engaging risk-reward experience.

### Core Mechanics

#### 1. Pace Per Second Growth
- **Pace** = Multiplier increase per second
- **Formula**: `Pace(t) = Pace(t-1) × (1 + Growth%)`
- **Example** (25% growth): Second 1: x, Second 2: x × 1.25, Second 3: x × 1.25²

#### 2. Accumulated Multiplier Calculation
- **Formula**: `Acc(t) = Base Floor + Σ Pace(i) for i=1→t`
- **Advanced Formula**: `result(time) = BaseMultiplier + (InitialGrowthStep / AccelRate) × ((1 + AccelRate)^time − 1)`
- **Example** (3.5 seconds): `Acc = Base + Pace1 + Pace2 + Pace3 + (Pace4 × 0.5)`

#### 3. Player Decision Mechanics
- **Claim Timing**: Players claim based on relative progress within the round
- **Formula**: `Claim Time = Progress × Duration`
- **Example**: 70% progress, 6-second duration → Claim at 4.2 seconds
- **Timeout Result**: Players who don't cash out receive **Base Floor Multiplier**

#### 4. Duration Distribution System
Round durations are sampled from configured probability distributions:
- 3 sec → 2.5%
- 4.5 sec → 20%
- 5.25 sec → 25%
- 6 sec → 30%
- (Additional durations per configuration)

## Business Goals

### Primary Objectives
- **Engagement**: Create suspenseful, skill-based gameplay through timing decisions
- **Revenue Generation**: Drive purchases through multiplier-based reward systems
- **Player Retention**: Balance risk-reward to maintain long-term engagement
- **Strategic Depth**: Reward player skill in timing and risk assessment

### Secondary Benefits
- **Personalization**: Segment-based configuration for different user types
- **Economy Control**: Fine-tune payout rates through multiple levers
- **Behavioral Insights**: Understand player risk tolerance and timing preferences

## Key Performance Indicators

### Core Metrics
- **Expected Value (EV)**: `Average(Claimed Multiplier)` across all players
- **Claim Rate**: Percentage of players who cash out vs. timeout
- **Average Claim Time**: Mean timing of player cash-out decisions
- **Timeout Rate**: Percentage of rounds ending in timeout (base floor payout)

### Engagement Metrics
- **Rounds per Session**: Player engagement with repeat gameplay
- **Progression Analysis**: How claim timing evolves with experience
- **Risk Behavior**: Distribution of claim timing across player base

### Economy Performance
- **Multiplier Distribution**: Analysis of actual vs. expected payouts
- **Segment Performance**: EV and behavior comparison across user segments
- **Duration Impact**: How round length affects player behavior and outcomes

## Economy Control Parameters

### Growth Configuration
- **Growth Percentage**: Fixed multiplier increase rate per second
- **Base Floor Multiplier**: Minimum payout for timeout scenarios
- **Initial Growth Step**: Starting pace value
- **Acceleration Growth Rate**: Exponential growth parameter

### Distribution Controls
- **Duration Distribution**: Probability weights for different round lengths
- **Max Multiplier**: Derived from `Duration × Pace Curve`
- **Fallback Duration**: Adjusted distribution after first-round timeout

### Segmentation Parameters
- **Player Segments**: Groups based on BI parameters (All-Users, FTUE, Dormants, etc.)
- **Per-Segment Controls**: Individual growth parameters, reward multipliers, duration distributions
- **Fallback Segment**: Default configuration (All-users) when no match found

## Leaderboard System

### Dynamic Statistics Generation
- **Source Data**: Max multipliers from completed rounds
- **Display Range**: x% to 100% of actual max multiplier per percentile
- **Statistics Tiers**: Top 1%, Top 5%, Top 10%, P75, P50, P25 (configurable)
- **Regeneration**: Updates after each mini-game completion (2-3 rounds)

### Purpose
- **Social Comparison**: Show relative performance against other players
- **Aspiration**: Create targets for improved performance
- **Engagement**: Encourage repeat play through competitive elements

## Timeout Mitigation Logic

### First Round Timeout Handling
- **Trigger**: Player receives base floor multiplier due to timeout
- **Response**: Next round may use fallback duration distribution
- **Goals**: 
  - Prevent repeated low outcomes
  - Maintain player engagement
  - Smooth difficulty spikes

## Configuration Validation Rules

### Required Validations
- **Default Segment**: One default segment required (All-users)
- **Segment Integrity**: No overlapping segment ranges
- **Parameter Minimums**: Base multiplier > 0, Growth pace > 0%, Initial Growth Step > 0
- **Probability Validation**: Each segment's duration probabilities must sum to 100%
- **Leaderboard Logic**: Each tier must be larger than the previous (hierarchical consistency)

## Analytical Focus Areas

### Player Behavior Analysis
- **Risk Tolerance**: Distribution of claim timing preferences
- **Learning Curves**: How player strategy evolves over time
- **Segment Differences**: Behavioral variations across user types

### Economy Optimization
- **EV Calibration**: Balancing player rewards with business objectives
- **Duration Impact**: Optimal round length distributions
- **Growth Rate Tuning**: Finding the sweet spot for engagement vs. payout

### Performance Monitoring
- **Timeout Patterns**: Identifying players struggling with timing
- **Multiplier Achievement**: Success rates for high-value outcomes
- **Session Analysis**: Multi-round engagement and progression patterns

## Comprehensive Feature Documentation

### **MGAP Replacement Strategy**
- **Purpose**: Replace/augment passive MGAP with interactive experience  
- **Configuration**: Can replace MGAP entirely or run alongside (configurable per offer/segment)
- **Value Proposition**: Player-controlled outcomes vs. fixed rewards, higher upside potential

### **Multi-Run System**
- **Structure**: Each session includes 2 consecutive runs with independent crash points
- **Final Reward**: Highest multiplier between runs (best result wins)
- **UI Flow**: Automatic progression from Run 1 to Run 2, final reward shown after completion
- **Fallback Logic**: If first run crashes early, second run may use adjusted duration distribution

### **Social & Competitive Layer**
- **Leaderboard**: Fully simulated (bot-based) showing top wins and player results
- **Dynamic Display**: Updates during entry/store, static during gameplay  
- **Multiplier Ranges**: Generated from 80%-100% of actual max multiplier per percentile
- **Competitive Pressure**: Creates aspiration and repeat purchase motivation

### **Monetization Integration**
- **Offer Attachment**: Configurable per offer/segment with visual indicators
- **Standalone Mode**: Can run as bonus game without purchase (using PO as base value)
- **Store Integration**: Visible on offer cards and main store button when active
- **Win Display**: Shows "Win up to" amounts with min/max multiplier ranges

### **Promotional Capabilities**

#### **Core Promotions**
- **Double Your Win**: Multiply final result by 2x
- **BOGO**: Extra mini-game for free (same base amount)  
- **Extra Run**: 3 runs instead of 2 for increased perceived value
- **Crash Insurance**: Increased base multiplier for safety
- **Bonus Rewards**: Milestone rewards at specific multiplier thresholds
- **High Multiplier Events**: Increased maximum multiplier caps

#### **Journey Integration**
- **Triggers**: Played Aviator, Player Crashes, Player Bought Aviator, Player Cashes Out
- **Conditions**: Crash patterns, cash-out thresholds, multiplier achievements
- **Source Filtering**: Payment-only triggers (exclude free sessions)

### **Technical Architecture**

#### **Configuration Management**  
- **Live Updates**: Real-time configuration changes without disrupting active sessions
- **Segmentation**: Fully segmented with fallback to default (All-users)
- **Session Length**: Configurable upper bound (initial default: 15 seconds)
- **Asset Management**: Dynamic assets grouped under "Feature" type in Asset Resource Manager

#### **Back Office Structure**
- **Two-Tab System**: Main Configuration + Promotions
- **Grid Management**: Status filtering, scheduling, priority assignment
- **Operations**: Enable/Disable, Edit, Clone, Delete with sticky action panel
- **Export Capability**: Configuration export to Excel

### **Player Experience Design**

#### **Core Gameplay Flow**
1. **Entry**: Post-purchase trigger with base value display
2. **Flight Start**: Manual start (paid) or automatic (bonus)  
3. **Real-time Multiplier**: Continuous growth with LOCK button
4. **Decision Point**: Player chooses when to cash out before crash
5. **Post-Lock Continuation**: Shows what would have happened if continued
6. **Winner Screen**: Final multiplier + coin calculation display

#### **Onboarding & Education**
- **First-Time Flow**: Forced video + info page + step-by-step guidance
- **Visual Feedback**: Plane takeoff, graph animation, win celebrations
- **Clear UI**: Large multiplier display, live coin calculation, responsive LOCK button

### **Customer Support Integration**
- **History Tracking**: Similar to MGAP with date/time, purchase type, run details
- **Session Details**: Multipliers per run, final result, crash status, crash multiplier
- **Bonus Tab**: Final coin rewards, SKU rewards, collectible details

### **Data & Analytics Framework**

#### **Streaming Events**
- **Purchase**: Aviator transaction with round distinction
- **Round Started**: Mini-game initiation
- **Round Ended**: Completion via timeout/leave  
- **User Rewarded**: Final reward distribution

#### **Key Tracking Fields**
- **Game Metrics**: Round duration, win multiplier, final multiplier, timeout status
- **Configuration Data**: Growth pace, base multiplier, segment ID
- **Behavioral Data**: Claim timing, leaderboard values, crash patterns
- **Revenue Data**: Transaction IDs, source amounts, final rewards

### **Risk Mitigation & Validation**
- **Guaranteed Base**: Always above purchase value (eliminates loss)
- **Server Control**: Crash logic controlled server-side for fairness
- **Transparency**: Visible player results increase trust
- **Balance Control**: Configurable parameters maintain economic stability

---
**Note**: Aviator represents the first implementation of crash/aviator mechanics in social casino, combining the $2-4B iGaming genre with social casino safety through guaranteed base rewards. This creates a skill-based risk-reward experience where player timing decisions directly impact outcomes, while comprehensive configuration systems allow for precise economy control and extensive promotional flexibility.
