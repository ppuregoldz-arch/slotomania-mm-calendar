# Slotomania Product Usage Analysis - Business Context

**Last Updated:** 2024-01-15  
**Version:** 1.0  
**Game:** Slotomania (Social Casino Game)

---

## Game Overview

### Slotomania Background
Slotomania is a social casino game where players spin slot machines using virtual coins. The game focuses on entertainment value rather than real money gambling, with players earning experience points (XP), progressing through levels, and unlocking new machines and features.

### Business Model
- **Free-to-Play:** Base game is free with virtual currency
- **In-App Purchases:** Players buy coin packages with real money
- **Social Features:** Friends can send bonuses and gifts
- **Progression System:** Level-based unlocks and tier advancement

---

## Core Business Metrics

### Revenue Metrics
- **ARPU** - Average Revenue Per User
- **ARPPU** - Average Revenue Per Paying User  
- **LTV** - Lifetime Value (total payments received from a user)
- **VFM / V4M (Value for Money)** - Exchange rate from USD to coins; depends on user tier & level

### User Engagement Metrics
- **DAU** - Daily Active Users
- **MAU** - Monthly Active Users
- **Churn Rate** - Percentage of DAU who stop returning to the app
- **Second-Day Retention** - Users who return one day after install

### Conversion Metrics
- **FTD** - First-Time Depositors
- **STD** - Second-Time Depositors
- **PU** - Paying Users

---

## Game Features & Products

### Core Gameplay Elements
- **Balance** - The amount of coins or other currency a user currently holds
- **XP (Experience Points)** - Earned by spinning; unlocks higher levels/machines
- **Big Win** - When a user wins ×5 or ×10 of their total bet
- **Mega Win** - When a user wins ×20 of their total bet
- **SP (Status Points)** - Points earned by purchasing in-game products

### Bonus & Gift Systems
- **Bonus** - A gift that the user can get from the game itself or from friends (e.g., coins)
- **FS** - Free Spins
- **Lucy Bonus** - Daily bonus in Slotomania given by Lucy via the GCP
- **GCP** - Gift Collection Pop-up
- **Turbo Bonus** - Super-bonus every 2 hours instead of 4

### Special Features
- **Piggi Bank** - Slotomania feature that saves a portion of each spin's coins into a bank the user can later buy
- **S&L** - Sneaks and Ladders feature
- **GM** - Game Mania event
- **SQ** - Sloto Quest
- **GS** - Golden Spin
- **HO** - Hidden Objects feature
- **Spinner Clash** - Slotomania tournament encouraging longer play; house adds % of wins to prize pot

---

## User Segmentation

### Player Tiers
User progression through tier system based on spending and engagement:

| Tier ID | Tier Name | Description |
|---------|-----------|-------------|
| 1 | Bronze | Entry-level players |
| 2 | Silver | Regular players |
| 3 | Gold | Engaged players |
| 4 | Platinum | High-value players |
| 5 | Diamond | Premium players |
| 6 | Royal Diamond | Elite players |
| 7 | Black Diamond | Top-tier players |

### Level Progression
- **Level System:** Players advance through levels by earning XP
- **Machine Unlocks:** Higher levels unlock new slot machines
- **Feature Access:** Certain features require minimum level thresholds

---

## Monetization Features

### Purchase Systems
- **PP (Payment Page)** - Where users buy coins
- **SKU** - Stock Keeping Unit / catalog ID for in-app items
- **PO (Personal Offer)** - Personalized offer based on user level and payment history
- **MGAP (Mini Game After Purchase)** - Optional mini-game offer after a user purchase, awarding extra coins percentage

### Promotional Systems
- **Coupon** - A mechanism to grant a user a bonus from the game
- **inApp** - In-application message pop-up shown to users for promos, features, issues, etc.
- **Sweepstake** - Marketing contest rewarding users (e.g., "Play bonus game today, win 1000 coins")

---

## Technical Infrastructure

### Data Systems
- **Vertica** - Column-store database for big-data analytics
- **Kafka** - Distributed messaging system; used at Playtika for inter-service comms and streaming history to DWH
- **Tableau** - Reporting/BI tool used by analytics team

### Identification Systems
- **GUID** - Unique Spin ID
- **SNID** - Social-Network ID linked to a user (e.g., Facebook ID)
- **Client Type** - A compound identifier for app+platform+device+SN+market (e.g., "Apple iPhone3", "Slotomania Yahoo Games‑Web")
- **Platform** - The framework/OS on which the app is played

### Business Operations
- **BO (Back Office)** - Internal system used mainly by Marketing & CRM to configure coupons, promotions, payment pages, etc.
- **CRM** - Customer Relationship Management
- **TRS (Total Rewards Social)** - Unified Playtika loyalty system

---

## Analysis Context for This Project

### Product Usage Focus
For this analysis, "products" refer to:
- **Slot Machines:** Individual game machines with different themes
- **Bonus Features:** Special gameplay elements and mini-games
- **Purchase Items:** Coin packages and special offers
- **Social Features:** Friend interactions and community elements

### Key Business Questions
1. **Usage Pattern Changes:** How has player engagement with different products shifted?
2. **Monetization Impact:** How do usage changes affect revenue and ARPPU?
3. **Value Perception:** Are players getting better or worse value for their money?
4. **Tier Behavior:** How do different player tiers respond to product changes?

### Success Metrics
- **Increased Engagement:** Higher session duration and interaction frequency
- **Improved Monetization:** Better ARPPU and conversion rates
- **Enhanced Value:** Better VFM ratios and user satisfaction
- **Balanced Growth:** Sustainable patterns across all user tiers

---

## Game Terminology Quick Reference

### Gameplay Terms
- **CZ** - Comfort Zone
- **CTR** - Click-Through Ratio
- **CTA** - Call to Action
- **MFE** - Machine Feature Engine
- **White Wedge** - Highest segment in the Mega Bonus
- **FTUE** - First-Time User Experience

### Offer System Terms
- **Template ID** - Unique identifier for a specific offer configuration
  - **Definition**: ID assigned to a specific offer targeting a specific segment, with specific configuration, for a specific promo date period
  - **Lifecycle**: Template IDs are provided by Ops team ONLY after the offer goes live
  - **Usage**: Essential for gatekeeping queries and offer validation across all features
  - **Timing**: Template IDs from previous analyses may be outdated if referring to past promo periods
  - **Examples**: `template_id = 221777` (RV offers), various IDs across Purchase Tools, Seasonals, etc.
  - **Cross-Squad Relevance**: Used across RV, Purchase Tools, Seasonals, Albums - any feature with offers

### Game Mechanics & Reward Systems
- **Wheel of Fortune/Hammers** - Secondary reward mechanism triggered by primary events (RV ads, purchases)
  - **Connection Chain**: Primary Event → Bonus Journey → Wheel Game → Actual Rewards
  - **Key Fields**: `game_guid`, `parent_reward_request_id`, `source_reward_id`
  - **Common SKU IDs**: 200143 (wheel trigger), 200173 (hammers), others for different reward types
- **Multi-Source Rewards** - Same reward type (hammers, coins) can come from multiple sources
  - **Challenge**: Distinguishing RV wheel hammers from purchase hammers, daily bonus hammers, etc.
  - **Solution**: Follow proper relational chains through game mechanics tables, not timing/session assumptions
- **Progressive Rewards** - Rewards that involve multiple steps or game mechanics beyond the initial trigger
  - **Tables**: `sm_external_progressive_jaw_game_played`, `fact_sm_goods_service_data`, bonus journey tracking
  - **Analysis Approach**: Trace through actual game flow rather than assuming direct connections

### Analytical Context
- **KPI** - Key Performance Indicator
- **Wiki** - Internal knowledge base (https://wiki.playtika.com)
- **PO (👥 Product Owner)** - Role: product stakeholder/manager

---

## Important Business Rules

### Value for Money (VFM)
- VFM rates vary by user tier and level
- Higher tier users often receive better coin-to-dollar ratios
- Personal offers typically provide enhanced VFM

### User Lifecycle
- New users start at Bronze tier, level 1
- Progression requires both XP (playing) and spending
- Different products unlock at different levels

### Revenue Recognition
- All revenue tracked in USD
- Coins are virtual currency with no cash value
- Status Points track loyalty but don't convert to cash

---

## References

### Additional Resources
- **Slotomania Wiki:** https://wiki.playtika.com/pages/viewpage.action?spaceKey=SLOT&title=Slotomania+Home
- **Data Dictionary:** documentation/data_dictionary.md
- **Analysis Methodology:** documentation/methodology.md

### Contact Points
- **Product Team:** For feature and gameplay questions
- **Analytics Team:** For data interpretation and validation
- **Business Intelligence:** For metric definitions and benchmarks

---
