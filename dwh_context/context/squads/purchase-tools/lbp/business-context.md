# LBP - Business Context

**Feature**: LBP (Lotto Bonus Premium)
**Purpose**: Purchase funnel optimization and conversion improvement through premium bonus upsell
**Note**: LBP is separate and distinct from Dice Deluxe feature

## Feature Overview

### Core Mechanics
- **Trigger**: Activated after **3 consecutive Special Bonus collections**
- **Base Experience**: **Lotto Bonus** (free version) 
- **Premium Upsell**: **Lotto Bonus Premium** with higher multipliers
- **Lobby Position**: Permanent static icon in lobby rotation

### Complex Multiplier System
LBP features a sophisticated 5-layer multiplier calculation:
- **Level Multiplier**: Player level-based enhancement (× 100)
- **Tier Multiplier**: Spending tier bonus ((tier + 1))
- **Segment Multiplier**: User segment classification multiplier  
- **Strong Ball Multiplier**: Special ball bonus mechanics
- **Ball Multipliers**: Sum of regular ball values

### Ball Mechanics
- **STRONG Balls**: Special high-value balls (avg ~15.86, median 12)
- **REGULAR Balls**: Standard 3-ball system (avg 8602, median 2600)
- **Ball Types**: Different multiplier ranges and frequencies

## Business Goals

### Primary Objectives
- **Conversion Optimization**: Drive free-to-premium upgrade after lotto experience
- **Revenue Enhancement**: Premium multipliers justify higher willingness to pay
- **Retention**: Integrate with Special Bonus collection cadence (3-hour cycle)
- **User Value**: Provide meaningful upgrade over free lotto experience

### Integration Strategy  
- **Special Bonus Dependency**: Leverages existing 3-hour collection habit
- **Premium Pattern**: Follows proven freemium-to-premium model (similar to Golden Spin after Mega Bonus)
- **Lobby Presence**: Permanent visibility ensures discoverability

## Key Performance Indicators

### Conversion Metrics
- **Free-to-Premium Conversion Rate**: Users and events conversion from free lotto to LBP purchase
- **Weekly Conversion Funnel**: Free lotto bonus impressions → LBP premium purchases
- **Revenue per Converting User**: Average LBP purchase value per upgrading user

### Engagement Metrics
- **Lotto Bonus Frequency**: Free lotto bonus participation rates
- **Special Bonus Integration**: Impact on 3-consecutive collection behavior
- **Retention**: Premium users vs free users retention comparison

### Quality Metrics
- **Multiplier Accuracy**: Mathematical validation of complex reward calculations
- **Ball Distribution**: STRONG vs REGULAR ball frequency and value distribution
- **Hourly Performance**: Lotto performance variation by hour of day

## Technical Architecture

### Primary Tables
- **`dwh.sm_fact_lotto_bonus`**: Core events and multiplier tracking
- **`dwh.fact_sm_bonus_history`**: Free lotto bonus triggers (bonus_type_id=32)
- **Payment Integration**: Product_Name ILIKE '%lbp%' for premium purchases

### A/B Testing Framework
Multiple sequential test phases:
- **Test 1**: No Bucks integration (Test ID: E61vWaMYAu)
- **Test 2**: Second No Bucks opening (sm_draft.nobucks_allocation_2025_02_20)
- **Test 3**: Multipliers optimization (sm_draft.final_allocation)

### Business Rules
- **Free Classification**: lotto_type = 'old' (freemium experience)
- **Premium Classification**: Other lotto_types (premium variants)
- **Quality Validation**: Built-in mathematical verification system

## Feature Ecosystem Integration

### Special Bonus Connection
- **Prerequisite**: Requires 3 consecutive Special Bonus collections
- **Cadence Alignment**: Integrates with 3-hour Special Bonus cycle
- **Cross-Feature Synergy**: Reinforces Special Bonus engagement

### Monetization Integration
- **Premium Upgrade Path**: Clear value proposition with higher multipliers
- **SKU Integration**: Standard (sku_id, transaction_source_type_id) product mapping
- **Purchase Tools Ecosystem**: Part of comprehensive conversion optimization suite

---
**Source**: Updated from Slotomania onboarding documentation and user-provided query analysis revealing complex multiplier mechanics and A/B testing framework.