# Parameter Validation Workflow

## Step 1 – Understand the Change

Before starting the validation, review:
- definition.md
- change-timeline.md
- Relevant historical change documents

Then understand:

### General Information
- Parameter name
- Business description
- Business purpose
- Parameter type
- Previous logic
- New logic
- Dependencies

### Identify:
- Which parameters are used to calculate this parameter
- Which parameters depend on this parameter
- Whether the change may impact other parameters

### Expected Impact
Understand:
- What is expected to change
- Which users should be affected
- Which users should not be affected

### Expected Population

At the end of this step, generate:

#### Business Description
A single sentence describing what the parameter represents and how it is used from a business perspective.

**Example:**
CZ represents the user's spending level and is used for segmentation and offer personalization.

#### Change Description
A single sentence describing the implemented change.

**Example:**
Lowered the minimum eCPM thresholds for DPU users across all CZ buckets in order to increase ad eligibility.

## Step 2 – Validate the Change

### Value Validation
Verify that:
- New values follow the new logic
- Previous values follow the previous logic
- Value transitions match expectations
- No unexpected NULL values were created
- No values exist that are not defined by the new logic

### Population Validation
Verify:
- Which users received new values
- Which users remained unchanged
- Users who should not have changed remained unchanged
- The affected population matches business expectations

Calculate:
- Expected Population
- Actual Population
- Absolute difference
- Percentage difference

### Dependency Validation
If dependent parameters exist:

Verify that:
- No unexpected side effects were introduced
- Related logic remains consistent
- No dependent processes or parameters were broken

Document all dependency checks performed.

### User-Level Validation
In addition to validating the entire population, select representative users and perform manual validation.

For each user provide:
- User ID
- Previous value
- New value
- A short explanation (one sentence) describing why the user received the new value according to the new logic

The final summary must explicitly include all manually validated users.

## Step 3 – Impact Analysis

### Mandatory Metrics
Present:
- Total affected users
- Percentage of affected users
- Total unaffected users
- Expected Population
- Actual Population
- Gap between expected and actual populations

### Continuous Numeric Parameters
Present a change distribution.

For example:
- Decrease greater than 20%
- Decrease between 10%-20%
- Decrease between 0%-10%
- No change
- Increase between 0%-10%
- Increase between 10%-20%
- Increase greater than 20%

Or any alternative grouping that better matches the parameter logic.

### Ordered Bucket Parameters
Present:
- Users moved up 1 bucket
- Users moved up 2 buckets
- Users moved up 3 buckets
- Users moved down 1 bucket
- Users moved down 2 buckets
- Users with no change

### Segmentation Parameters
Present a Transition Matrix:

| Previous Value | New Value | Users |
|---------------|-----------|-------|
| NPU | DPU | X |
| DPU | DDPU | Y |

All observed transitions should be included.

### Boolean Parameters
Present:

| Previous Value | New Value | Users |
|---------------|-----------|-------|
| False | True | X |
| True | False | Y |

### Visualization
Generate a table and/or chart describing the change according to the parameter type.

## Step 4 – Summary

Generate a concise summary in bullet points.

### General Information
- Parameter name
- Business description (one sentence)
- Validation date

### Change Description
- Short description of the implemented change
- Intended target population

### Results
- PASS / FAIL
- Number of affected users
- Expected Population
- Actual Population
- Gap between expected and actual populations
- Detected anomalies
- Unexpectedly affected populations

### Root Cause Analysis (if required)
If anomalies were identified, describe:
- The issue detected
- The most likely cause
- Whether it is caused by the new logic
- Whether it is caused by source data
- Whether it is caused by a dependent parameter that was not updated
- Any other relevant explanation

### Validation Examples
Include:
- List of validated User IDs
- Previous value
- New value
- Short explanation of why the new value was assigned

## Documentation

Every validation must be documented.

### Folder structure:
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

### Documentation Rules
- Each parameter must have its own dedicated folder.
- Existing historical information must never be deleted.
- Existing documentation files should be updated with new information.
- Every new change must be documented under the changes folder.
- change-timeline.md must be updated with a summary of the new change.
- Relevant charts, tables, and validation results should be preserved as part of the documentation.

## Required Final Output

Every validation run must end with a structured **Validation Report** containing:

- Business description of the parameter.
- Description of the implemented change.
- Expected Population.
- Actual Population.
- Value validation results.
- Population validation results.
- Dependency validation results.
- Impact analysis.
- Relevant tables and charts.
- Manually validated user examples.
- Detected anomalies and Root Cause Analysis when applicable.
- Final conclusion: PASS / FAIL.