# Figz - Business Context

## Feature Overview
**Figz** is a mid-term collection feature where players collect figure coins through spinning gameplay, purchase figures to build themed sets, and receive free spin rewards upon set completion. The feature combines collection mechanics with direct monetization through figure purchases and gem-based bundle upgrades.

## Core Mechanics

### Figure Collection System
- **Figure Coin Earning**: Coins collected through regular spinning gameplay on designated machines
- **Figure Purchase**: Players buy individual figures using collected coins
- **Set Completion**: Complete themed figure sets to unlock reward packages
- **Free Spin Rewards**: Set completion grants free spin bonuses and other rewards

### Bundle System
- **Bundle Creation**: Figured-themed lootbox bundles available for purchase
- **Bundle Types**: Multiple bundle tiers (Silver Lion, Gorilla, and other themed options)
- **Gem Upgrades**: Players can spend gems to upgrade bundles for enhanced rewards
- **Event Source Integration**: Bundles created through internal-purchase system

### Set Structure
- **Themed Sets**: Figures organized into thematic collections
- **Completion Tracking**: Progress monitoring for individual sets and overall collection
- **Reward Distribution**: Set-specific rewards with increasing value for larger sets
- **Collection Goals**: Multiple sets providing varied completion objectives

## Business Goals

### Primary Objectives
- **Mid-term Engagement**: Provide 1-4 week engagement cycle between major features
- **Collection Monetization**: Drive revenue through figure purchases and bundle upgrades
- **Gameplay Integration**: Enhance spinning gameplay with collection objectives
- **Player Retention**: Medium-term goals maintaining interest during content gaps

### Strategic Value
- **Incremental Revenue**: Additional monetization stream through collection mechanics
- **Engagement Bridging**: Maintain player activity between seasonal content updates
- **Feature Variety**: Provide different engagement type from daily challenges and seasonal events
- **Gem Economy Contribution**: Bundle upgrades provide consistent gem spending opportunities

## Key Performance Indicators (KPIs)

### Collection Metrics
- **Figure Coin Earning Rate**: Collection velocity through gameplay
- **Set Completion Rate**: % of participants completing full figure sets
- **Collection Duration**: Average time from start to set completion
- **Multi-Set Engagement**: Players completing multiple sets during feature period

### Monetization Metrics
- **Bundle Creation Rate**: % of participants purchasing figure bundles
- **Gem Upgrade Conversion**: Bundle upgrade rate using gem spending
- **Revenue per Participant**: Average spending by engaged Figz players
- **Bundle Type Performance**: Revenue comparison across different bundle tiers

### Engagement Metrics
- **Feature Participation Rate**: % of active players engaging with Figz
- **Daily Collection Activity**: Sustained engagement throughout feature period
- **Cross-Feature Impact**: Figz engagement effect on other game areas
- **Return Rate**: Player re-engagement in subsequent Figz feature cycles

## Technical Architecture

### Data Systems
- **`dwh.sm_fact_lootbox_history_hero`**: Bundle creation and upgrade event tracking
- **`sm_Draft.figz_dates`**: Feature availability period management (ts_from, ts_to)
- **Event Tracking**: BOX_CREATED and BOX_UPGRADED event monitoring
- **Set Progress Tables**: Individual figure and set completion tracking

### Bundle Economics
- **Bundle Types**: slotoheroes_silverlion, slotoheroes_gorilla configurations
- **Upgrade Mechanics**: Gem-based bundle enhancement system
- **Revenue Attribution**: Bundle purchase and upgrade revenue tracking
- **Event Source Validation**: internal-purchase source verification

## Feature Integration

### Core Gameplay Integration
- **Spinning Integration**: Figure coins earned through designated machine play
- **Reward Integration**: Free spin rewards distributed through existing reward systems
- **Progress Display**: Set completion progress visible in game interface

### Economic Integration
- **Gem Economy**: Bundle upgrades provide gem spending opportunities
- **Reward Economy**: Set completion rewards integrated with main game economy
- **Purchase Integration**: Figure bundles available through standard purchase systems

## Risk Areas & Monitoring

### Collection Balance
- **Earning Rate Balance**: Figure coin acquisition rate calibration
- **Completion Difficulty**: Ensure achievable set completion for engaged players
- **Reward Value**: Set completion rewards must justify collection investment

### Monetization Health
- **Bundle Value Proposition**: Clear benefits for bundle purchases and upgrades
- **Gem Economy Impact**: Bundle upgrades' effect on overall gem spending patterns
- **Revenue Sustainability**: Consistent monetization across multiple Figz cycles