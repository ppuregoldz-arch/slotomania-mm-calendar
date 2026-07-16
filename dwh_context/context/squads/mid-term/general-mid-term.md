# General Mid-term System - Business Context

## Feature Overview
**Mid-term Features** are rotating engagement systems that run for 1-4 weeks, positioned between short-term daily features and long-term seasonal content. These features provide content variety, maintain player interest during content gaps, and offer incremental monetization opportunities through specialized mechanics and progression systems.

## Core Mid-term Feature Types

### Collection-Based Features
- **Figs (Figz)**: Collect figure coins through spinning, purchase figures to complete sets for free spin rewards
- **Globez**: Collect snow globes from different regions (USA/AUS/JPN/FRA sets) via designated games for coin grab rewards
- **Mega Pods**: Earn pods from Mega wins with rarity-based timers, instant unlock with gems (max 4 stored, 1 active)

### Activity-Based Features
- **Winovate**: Spend hammers to renovate items across scenes, featuring Hammer Strike minigame with hammers earned from designated games
- **Stash or Splash**: Race across missions against other players for pooled grand prizes with prize splitting on multiple winners

### Progressive Systems
- **Dynamic Jackpots**: Multi-stage progressive jackpot systems with enhanced payout mechanics
- **Bar Progression**: Progressive reward systems with incremental milestone unlocking
- **Participation Features**: Community-wide engagement mechanics with shared objectives

## Business Goals

### Primary Objectives
- **Engagement Bridging**: Maintain player interest between major seasonal events and content updates
- **Content Freshness**: Regular rotation prevents feature fatigue and keeps gameplay feeling new
- **Incremental Monetization**: Additional revenue streams through feature-specific purchases and accelerators
- **Player Segmentation**: Different features appeal to different player types and engagement patterns
- **Retention Enhancement**: Consistent mid-term goals provide medium-term play motivation

### Strategic Value
- **Content Pipeline Management**: Systematic content delivery preventing engagement gaps
- **Revenue Diversification**: Multiple monetization vectors reducing dependence on core features
- **Feature Testing Ground**: Mid-term features serve as testing environment for new mechanics
- **Community Engagement**: Shared objectives and competition foster community interaction
- **Cross-Feature Integration**: Mid-term features enhance and interact with existing core systems

## Key Performance Indicators (KPIs)

### Engagement Metrics
- **Participation Rate**: % of active players engaging with mid-term features
- **Feature Duration Engagement**: Average days of participation per feature cycle
- **Cross-Feature Interaction**: Mid-term feature impact on other game area engagement
- **Retention During Feature**: Player retention rates during mid-term feature periods
- **Return Rate Post-Feature**: Player comeback rate after feature conclusion

### Collection & Progression Metrics
- **Collection Completion Rate**: % of participants completing full sets/objectives
- **Progress Velocity**: Speed of progression through feature milestones
- **Set/Milestone Distribution**: Player distribution across completion levels
- **Collection Drop-off Points**: Identification of engagement decline stages

### Monetization Metrics
- **Feature-Specific Revenue**: Direct purchases and gem spending within features
- **Accelerator Usage**: Gem spending on instant unlocks and progression boosts
- **Bundle/Package Sales**: Revenue from feature-themed purchase packages
- **Revenue per Participant**: Average spending by engaged mid-term feature players
- **Cross-Feature Revenue Impact**: Mid-term engagement driving spending elsewhere

## Technical Architecture

### Rotation Management System
- **Feature Scheduling**: Systematic deployment and rotation timing
- **Overlap Management**: Coordination with seasonal features and major events
- **Performance Monitoring**: Real-time engagement and revenue tracking
- **A/B Testing Framework**: Feature variant testing and optimization

### Core Data Systems
- **`dwh.sm_fact_lootbox_history_hero`**: Figz bundle creation and upgrades
- **`sm_fact_mega_win_party_history`**: Mega Pods collection and unlock events
- **Feature-Specific Tables**: Dedicated tracking for each mid-term feature type
- **Integration Tables**: Cross-feature interaction and impact tracking

### Integration Architecture
- **Core Game Integration**: Seamless interaction with spinning, winning, and progression
- **Economy Integration**: Feature currencies and rewards integrated with main economy
- **Purchase Integration**: Feature-specific offers and accelerators through existing payment systems
- **Analytics Integration**: Unified tracking and reporting across all mid-term features

## Feature Ecosystem Integration

### Core Game Mechanics
- **Spinning Integration**: Many features triggered by or enhanced through regular gameplay
- **Win-Based Triggers**: Features activated by specific win types or amounts (Mega wins, designated games)
- **Progressive Integration**: Mid-term progression complementing core progression systems

### Economic Integration
- **Gem Economy**: Mid-term features provide consistent gem spending opportunities
- **Coin Economy**: Feature rewards contribute to player coin balance and economy
- **Purchase Integration**: Feature-themed offers and bundles enhance monetization

### Cross-Feature Synergy
- **Seasonal Coordination**: Mid-term features complement rather than compete with seasonal content
- **Daily Feature Enhancement**: Mid-term objectives can enhance daily challenge systems
- **Long-term Integration**: Mid-term engagement supporting album collection and other long-term goals

## Risk Areas & Monitoring

### Feature Balance
- **Engagement vs. Fatigue**: Balance feature frequency with player capacity for engagement
- **Monetization Pressure**: Ensure mid-term features enhance rather than pressure player experience
- **Completion Accessibility**: Maintain achievable progression paths for different player types

### System Integration
- **Feature Overlap Management**: Prevent overwhelming players with too many concurrent mid-term features
- **Economy Impact**: Monitor mid-term feature rewards' effect on overall game economy
- **Cross-Feature Cannibalization**: Ensure mid-term features complement rather than compete with core systems

### Long-term Health
- **Rotation Sustainability**: Maintain player interest across multiple feature cycles
- **Content Pipeline**: Ensure consistent pipeline of fresh mid-term content
- **Player Segment Balance**: Different features serving different player engagement preferences