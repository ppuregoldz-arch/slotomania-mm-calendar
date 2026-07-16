# Parameter Business Context

## Purpose

This skill is designed to validate parameter changes before production deployment, ensuring that the change was implemented correctly according to the business and technical logic, and does not introduce unexpected impact on users or dependent systems.

## Validation Goals

- Verify that the new parameter values were calculated and applied correctly according to the new logic.
- Verify that the intended population received the change.
- Verify that users who should not be affected remained unchanged.
- Quantify and describe the impact of the change on the population.
- Identify anomalies and potential issues before production deployment.
- Generate structured documentation for future reference, auditing, and troubleshooting.

## Business Context

A parameter is a calculated value assigned to each user based on predefined business logic.

Each user receives a single value for each parameter.

Parameter values may be:
- Numeric (Integer / Float)
- Categorical (String / Varchar)
- Boolean (True / False)
- Any other supported data type

Parameters are used to characterize users based on behavior, business value, or other attributes, enabling:
- User segmentation
- Personalized configurations and experiences
- Behavioral analysis
- Product and business decision-making

Parameters are calculated and stored in the Datamining table.

For pre-production validation, the expected change should appear in today's Datamining snapshot.

## Knowledge Base Usage

Before performing any validation, locate the parameter documentation under:

```
context/business-knowledge/parameters/
```

Parameter structure:

```
context/business-knowledge/parameters/
│
├── <parameter_name>/
│   ├── definition.md
│   ├── change-timeline.md
│   └── changes/
│       ├── YYYY-MM-DD-change-description.md
│       └── ...
```

### definition.md

Contains all permanent knowledge related to the parameter.

Use it to understand:
- Business description
- Business purpose
- Parameter type
- Calculation logic
- Parameter generation query
- Meaning of possible values
- Dependencies on other parameters
- Parameters that depend on it
- Primary business use cases

### change-timeline.md

Contains the history of all changes made to the parameter.

Use it to:
- Understand previous changes
- Identify similar historical changes
- Learn from previous validations

### changes/

Contains detailed documentation for each parameter change.

Use it to:
- Review previous validations
- Compare against historical results
- Identify recurring issues
- Use previous examples as reference points

## Parameter Types

Before starting validation, identify the parameter type and the appropriate analysis method.

### 1. Continuous Numeric Parameter

**Examples:**
- cz_price_cut_test
- simple_median_bet
- RV_opportunistic_dynamic_ecpm

**Characteristics:**
- Numeric value
- Magnitude of change is meaningful
- Percentage change can be calculated
- The primary analysis focuses on value differences and distribution shifts

**Example presentation:**
- +5%
- +10%
- -20%

**Validation expectations:**
- Measure percentage change between old and new values
- Analyze distribution of changes across the population
- Identify users with significant increases or decreases
- Quantify affected users by change range

**Typical output:**

| Change Range | Users |
|--------------|-------|
| Decrease >20% | X |
| Decrease 10%-20% | Y |
| No Change | Z |
| Increase 0%-10% | A |
| Increase >10% | B |

### 2. Ordered Bucket Parameter

**Examples:**
- rv_opportunistic_config_buckets
- precious_level

**Characteristics:**
- Values have a defined hierarchy and order
- Movement between buckets can be measured
- The distance between buckets is meaningful

**Example presentation:**
- No change
- Moved up 1 bucket
- Moved up 2 buckets
- Moved down 1 bucket

**Validation expectations:**
- Measure movement between buckets
- Quantify users moving up and down
- Identify the magnitude of movement
- Validate that transitions match the expected business logic

**Typical output:**

| Bucket Movement | Users |
|----------------|-------|
| Up 3 Buckets | X |
| Up 2 Buckets | Y |
| Up 1 Bucket | Z |
| No Change | A |
| Down 1 Bucket | B |
| Down 2 Buckets | C |

### 3. Segmentation Parameter

**Examples:**
- rv_segment_opportunistic
- DPU_Segment

**Characteristics:**
- Categories have no numeric meaning
- Movement between categories is meaningful
- Analysis focuses on transitions between segments

**Example presentation:**
- NPU → DPU
- DPU → DDPU
- Active → Dormant

**Validation expectations:**
- Build a transition matrix between old and new values
- Quantify users moving between segments
- Validate that transitions align with the new logic
- Identify unexpected segment assignments

**Typical output:**

| Previous Segment | New Segment | Users |
|------------------|-------------|-------|
| NPU | DPU | X |
| DPU | DDPU | Y |
| Active | Dormant | Z |

### 4. Boolean Parameter

**Examples:**
- eligible
- feature_enabled

**Characteristics:**
- Only two possible values

**Example presentation:**
- False → True
- True → False

**Validation expectations:**
- Quantify users who changed state
- Validate eligibility changes against the expected logic
- Verify that unaffected users remained unchanged

**Typical output:**

| Previous Value | New Value | Users |
|----------------|-----------|-------|
| False | True | X |
| True | False | Y |

If a parameter does not clearly fit one category, identify the dominant business interpretation and choose the most appropriate analysis methodology accordingly.