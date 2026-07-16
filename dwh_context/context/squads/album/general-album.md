# General Album System - Business Context

## Feature Overview
**Sloto Cards** is Slotomania's core collectible album system running in **70-day seasons**. Players collect cards to complete sets and albums, earning rewards for progression milestones. The system drives engagement through collection mechanics, completion incentives, and strategic card acquisition via multiple channels.

## Core Mechanics

### Card Collection System
- **Album Structure**: Cards organized into thematic sets within seasonal albums
- **Collection Period**: 70-day seasons with complete album reset
- **Completion Rewards**: Set completion and full album completion bonuses
- **Progression Tracking**: Visual progress indicators showing missing cards per set

### Card Types & Rarity
- **Regular Cards**: Standard collectible cards earned through gameplay
- **Gold Cards**: Premium non-tradable cards from special sources
- **Ace Cards**: High-value cards from exclusive channels, feed into Ace Spin Machine
- **Fusion Cards**: Enhanced cards created by combining 1 regular + 3 duplicate cards
- **Shiny Cards**: Special rarity exclusively from Shiny Show minigame
- **Wild Cards**: Universal completion cards for any missing slot

### Card Acquisition Channels
- **Gameplay Rewards**: Cards earned through spins, bonuses, challenges
- **Daily Dash Integration**: Cards as progression rewards and completion bonuses
- **Purchase**: Card packs available through Payment Page and Gems
- **Challenge Rewards**: Cards from seasonal features and mini-games
- **Gift Card Path**: Special promotional card distributions

## Business Goals

### Primary Objectives
- **Long-term Retention**: 70-day engagement cycle keeps players returning
- **Collection Completion Drive**: Near-completion urgency increases session frequency
- **Monetization via Scarcity**: Missing cards create purchase motivation
- **Cross-feature Engagement**: Album integration drives participation in other features

### Strategic Value
- **Retention Anchor**: Always-on progression system provides daily play motivation
- **Monetization Bridge**: Card packs and Wild Cards convert collection desire to revenue
- **Engagement Distribution**: Spreads player activity across multiple game features
- **Seasonal Content Framework**: Regular 70-day refresh keeps content feeling new

## Key Performance Indicators (KPIs)

### Collection Metrics
- **Set Completion Rate**: % of active players completing individual card sets
- **Album Completion Rate**: % of players finishing full 70-day album
- **Cards per DAU**: Average card acquisition rate per active user
- **Collection Velocity**: Time to completion for engaged collectors
- **Missing Card Distribution**: Analysis of bottleneck cards preventing completion

### Engagement Metrics
- **Collection Session Length**: Extended play time during card acquisition
- **Return Rate**: Player comeback rate during album season
- **Cross-feature Participation**: Album-driven engagement with Daily Dash, challenges
- **Near-completion Behavior**: Activity surge when close to set/album completion

### Monetization Metrics
- **Card Pack Revenue**: Direct purchase revenue from card acquisition
- **Wild Card Spend**: Gem spending on universal completion cards
- **Gem-to-Card Conversion**: Efficiency of gem spending on card progression
- **Completion Purchase Rate**: % of near-completers who buy missing cards
- **Revenue per Collector**: ARPPU specifically from collection-motivated purchases

## Technical Architecture

### Core Data Tables
- **`dwh.sm_fact_collectibles_cards`**: Primary card acquisition events
- **Card Ownership Tracking**: Player inventory and completion status
- **Set Progress Analytics**: Real-time completion percentage calculations
- **Wild Card Usage**: Universal card application events

### Integration Points
- **Daily Dash Rewards**: Card rewards integrated into challenge progression
- **Payment Page Integration**: Card packs as purchaseable products
- **Gem Store Integration**: Wild Cards available for gem purchase
- **Challenge System**: Seasonal features grant album-specific cards
- **Shiny Show Connection**: Exclusive channel for Shiny card acquisition

## Feature Ecosystem Integration

### Daily Dash Synergy
- **Reward Integration**: Cards as Daily Dash progression rewards
- **Wild Card Completion**: Daily Dash Max can grant Wild Cards
- **Engagement Multiplication**: Both features drive daily return behavior

### Monetization Integration
- **Gem Economy**: Wild Cards create consistent gem sink
- **Payment Page Products**: Card packs as purchaseable coin package additions
- **Personal Offers**: Targeted card completion offers for near-finishers

### Seasonal Features
- **Themed Cards**: Album seasons align with seasonal content themes
- **Special Card Channels**: Seasonal features grant exclusive album cards
- **Cross-promotional Content**: Album completion enables seasonal feature access

## Risk Areas & Monitoring

### Collection Balance
- **Completion Rate Monitoring**: Ensure reasonable but challenging completion rates
- **Card Distribution Fairness**: Prevent excessive bottleneck cards
- **Wild Card Economy**: Balance between scarcity and accessibility

### Engagement Sustainability
- **Season Fatigue**: Monitor player burnout across 70-day cycles
- **Collection Pressure**: Balance urgency with positive player experience
- **New Player Onboarding**: Ensure album system doesn't overwhelm newcomers

### Monetization Health
- **Purchase Pressure Monitoring**: Avoid overly aggressive monetization tactics
- **F2P Completion Path**: Maintain viable free-to-play progression
- **Revenue Sustainability**: Balance short-term card revenue with long-term retention