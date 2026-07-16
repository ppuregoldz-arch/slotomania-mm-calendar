# Counter PO - Business Context

**Feature**: Counter PO (Counter Purchase Offers)
**Purpose**: Limited inventory offer system with controlled scarcity and exposure management

## Feature Overview

Counter PO is an offer system that creates scarcity through **limited purchase availability** combined with **time constraints**. The feature controls both offer exposure and purchase volume through sophisticated group-based sequencing.

### Core Mechanism

**Dual Removal Triggers**: The offer is removed when either condition is met:
1. **Counter reaches zero** - All available purchases have been sold
2. **Timer expires** - Time limit for the offer has been reached

### Sequential Group System

**Group-Based Exposure Control**: 
- Multiple groups can be defined (e.g., 8 groups)
- Each group receives an offer with its own counter (e.g., 150 purchases per group)
- **Only one group is active at a time**
- Groups open sequentially - next group opens automatically when current group closes

**Group Closing Triggers**: A group closes when either condition is met:
1. **Sold out** - Counter reaches zero (all purchases completed)
2. **Impression limit reached** - Maximum distinct users exposed to the offer

## Business Goals

### Primary Objectives
- **Scarcity Creation**: Drive urgency through limited purchase availability
- **Exposure Control**: Manage offer visibility through sequential group activation
- **Revenue Optimization**: Balance scarcity with sufficient exposure for revenue generation
- **User Experience**: Provide clear feedback on offer availability and time constraints

### Secondary Benefits
- **A/B Testing Capability**: Test different counter sizes, impression limits, and group sequences
- **Risk Mitigation**: Control exposure volume to prevent over-exposure or under-monetization
- **Behavioral Insights**: Understand user response to scarcity-based offers

## Key Performance Indicators

### Conversion Metrics
- **Group conversion rate**: Purchases per impression by group
- **Overall conversion rate**: Total purchases across all groups
- **Time-to-purchase**: Speed of purchase decisions under scarcity pressure

### Scarcity Effectiveness  
- **Sell-out rate**: Percentage of groups that reach counter zero vs. impression limit
- **Timer vs counter completion**: Which trigger closes groups more frequently
- **Group progression speed**: Time between group activations

### Exposure Management
- **Impression utilization**: Actual vs. target impressions per group
- **Group activation patterns**: Sequential flow and timing analysis
- **User reach**: Distinct users exposed across all active groups

## Configuration Parameters

### Group Closing Controls
- **Impression limit**: Maximum distinct users who see the offer per group
- **Counter limit**: Maximum purchases available per group before sell-out

### Exposure Controls  
- **Number of groups**: Total groups that will be activated sequentially
- **Counter size**: Purchase inventory allocated to each group
- **Impression limit per group**: Exposure cap for each group
- **Offer timer duration**: Time limit for entire offer availability

## Analytical Focus Areas

### Performance Analysis
- Group-by-group performance comparison
- Conversion rate optimization by configuration
- Revenue per impression and revenue per group analysis

### User Behavior Analysis
- Response patterns to scarcity indicators (counter visibility)
- Time-based purchasing behavior (timer pressure)
- Repeat exposure and cross-group user behavior

### Configuration Optimization
- Optimal counter sizes for different user segments
- Impression limit calibration for maximum conversion
- Group sequencing strategy effectiveness

---
**Note**: This feature creates controlled scarcity through sequential group exposure, balancing user reach with purchase urgency to optimize both conversion rates and overall revenue generation.