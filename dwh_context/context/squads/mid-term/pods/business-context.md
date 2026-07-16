# Mega Pods - Business Context

## Feature Overview
**Mega Pods** is a mid-term collection feature where players earn pods from Mega wins, with rarity-based timers determining collection readiness. Players can store up to 4 pods with 1 active, and can spend gems for instant unlocking, creating a strategic collection and monetization system.

## Core Mechanics

### Pod Acquisition System
- **Mega Win Triggers**: Pods earned specifically from Mega win events during gameplay
- **Rarity-Based Timers**: Different pod rarities have varying collection timers
- **Storage Limitations**: Maximum 4 pods can be stored, with 1 pod active for collection
- **Queue Management**: Strategic decisions about which pods to keep and collect

### Unlock Mechanics
- **Time-Based Collection**: Standard collection after timer completion
- **Instant Unlock**: Gem spending for immediate pod collection
- **Season End Collection**: Automatic collection of remaining pods at feature end
- **Collection Status Tracking**: Detailed status progression monitoring

### Pod Types & Rarity
- **Chest Type Variations**: Different pod types with varying reward values
- **Rarity Timer Correlation**: Higher rarity pods require longer collection times
- **Reward Scaling**: Pod value increases with rarity and collection difficulty
- **Strategic Value**: Players balance rarity vs. collection timing decisions

## Business Goals

### Primary Objectives
- **Mega Win Enhancement**: Add excitement and value to high-value win events
- **Gem Monetization**: Create compelling gem spending opportunities through instant unlocks
- **Collection Strategy**: Engage players in strategic thinking about pod management
- **Mid-term Retention**: Provide ongoing collection goals over feature duration

### Strategic Value
- **Win Event Amplification**: Transform big wins into extended engagement opportunities
- **Monetization Layer**: Add revenue potential to existing high-engagement moments
- **Strategic Depth**: Collection and timing decisions create gameplay sophistication
- **Retention Bridge**: Pod collection goals maintain engagement between other content

## Key Performance Indicators (KPIs)

### Collection Metrics
- **Pod Earning Rate**: Mega Pods generated per active player
- **Collection Completion Rate**: % of earned pods successfully collected
- **Storage Utilization**: Average pod storage occupancy and queue management
- **Rarity Distribution**: Pod type distribution and collection patterns

### Monetization Metrics
- **Instant Unlock Rate**: % of pods unlocked using gem spending
- **Gem Spend per Pod**: Average gem cost for instant unlock behavior
- **Revenue per Participant**: Total gem spending by engaged Mega Pods players
- **Unlock Timing Analysis**: When players choose instant vs. time-based collection

### Strategic Engagement Metrics
- **Pod Queue Management**: Player behavior around storage limitations
- **Opt-out Rate**: Players choosing to skip or ignore pod opportunities
- **Multi-Pod Collection**: Players maintaining multiple pods simultaneously
- **Season End Collection**: Pods collected automatically vs. actively managed

## Technical Architecture

### Core Data Systems
- **`sm_fact_mega_win_party_history`**: Primary pod tracking with status progression
- **Status Types**: COLLECTED, COLLECTED_SEASON_END_REWARD, IMMEDIATELY_UNLOCK
- **Chest Type Management**: Different pod types with associated timer and reward values
- **Timestamp Tracking**: Precise timing for pod creation, timer, and collection events

### Pod State Management
- **Status Progression**: Created → Active Timer → Ready for Collection → Collected
- **Gem Unlock Events**: IMMEDIATELY_UNLOCK status for gem-based collection
- **Season End Processing**: COLLECTED_SEASON_END_REWARD for automatic cleanup
- **Storage Queue**: 4-pod maximum with active pod designation

### Revenue Attribution
- **Gem Spending Tracking**: Direct attribution of instant unlock gem costs
- **Pod Value Analysis**: Reward value comparison across collection methods
- **Cross-Feature Impact**: Mega Pods engagement effect on other game areas

## Feature Integration

### Mega Win Integration
- **Trigger Integration**: Pod earning triggered by existing Mega win mechanics
- **Reward Enhancement**: Pods add value layer to high-excitement win moments
- **Win Celebration**: Pod earning extends positive feeling from big wins

### Gem Economy Integration
- **Instant Unlock Monetization**: Strategic gem spending for immediate gratification
- **Value Proposition**: Clear benefit demonstration for gem investment
- **Economic Balance**: Pod unlock costs calibrated with gem economy health

### Storage & UI Integration
- **Visual Queue Management**: Clear display of pod storage and timer status
- **Strategic Decision Support**: Information to help players make collection choices
- **Notification Systems**: Timer completion and collection opportunity alerts

## Risk Areas & Monitoring

### Collection Balance
- **Timer Calibration**: Ensure reasonable collection times across rarity levels
- **Storage Pressure**: Balance storage limitations with player satisfaction
- **Opt-out Prevention**: Avoid overwhelming players with too many pod decisions

### Monetization Health
- **Gem Price Balance**: Instant unlock costs must provide clear value
- **Collection vs. Purchase Balance**: Maintain viable free collection path
- **Revenue Sustainability**: Consistent monetization across pod feature cycles

### Player Experience
- **Decision Complexity**: Avoid overwhelming casual players with strategic complexity
- **Reward Satisfaction**: Pod collection rewards must justify investment time or gems
- **Feature Integration**: Ensure Mega Pods enhance rather than interrupt core gameplay