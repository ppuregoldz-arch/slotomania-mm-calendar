# Operation - Monetization: Monday board contract

**Last verified:** July 2026  
**Purpose:** Technical contract for reading and safely writing Slotomania operational tasks.

## Board identity and authority

| Object | ID | Name / role |
|---|---:|---|
| Main board | `2109172490` | `Operation - Monetization` |
| Working view | `57490550` | The view used by Monetization and Ops |
| Subitem board | `2109172677` | `Subitems of Operation - Monetization` |

- The board URL is `https://playtika.monday.com/boards/2109172490/views/57490550`.
- `57490550` is a **view ID**, not a board ID.
- Read the live board to learn historical execution. Never alter it unless Itay explicitly asks.
- Operational work is normally a **subitem under the parent day** (`YYYY-MM-DD`), not a new top-level item in an offer-template group.
- The MM calendar says what should run. This board says how Ops should execute it.

## Main-board groups

### Template sources

| Group ID | Title |
|---|---|
| `group_mkv12864` | Buy All |
| `group_mm4h2685` | Limited PO |
| `group_mkv1971m` | Daily Deal |
| `group_mkzvt95x` | Triple Offer- Decoy |
| `group_mm0928d4` | Triple Offer- Equal offers |
| `group_mkv1q8yw` | RYD |
| `group_mkv1b6ky` | Rolling Offer |
| `group_mm15y5em` | PO ADS |
| `group_mkx57gcq` | Album handover |
| `group_mkv1vqxx` | MGAP |
| `group_mky2tww7` | Mid Term |
| `group_mkwyppjf` | Old Configs |
| `group_mkvw28e3` | Configs Gem EQ |
| `new_group30880` | Used templates |

Template groups are reference libraries. Do not place a dated production task there.

### Daily workflow

| Group ID | Title | Use |
|---|---|---|
| `group_mm0t6mxh` | Monday days | Current day parents and their operational subitems |
| `group_mkzhwecm` | Monday dates | Older day-parent group; read for history |
| `new_group3154` | Next Month Tasks from Template | Legacy/preparation tasks; not the default placement |
| `group_mkt4f0vq` | Ops Tasks Backlog | Unscheduled operational requests |
| `new_group` | DONE | Completed top-level work |
| `group_mkvt20ma` | Archive | Archived work |

## Main-board columns

| Column ID | Title | Type |
|---|---|---|
| `name` | Name | name |
| `status_15` | Status | status |
| `color_mkws7ys7` | Was QAed? | status |
| `color_mkv5jjn5` | Status | status |
| `people_1` | Assignee | people |
| `people99` | Owner | people |
| `date4` | Due Date | date |
| `date0` | Promo End Date | date |
| `long_text` | Description | long_text |
| `files` | Files | file |
| `connect_boards18` | Economy Tasks | board relation |
| `connect_boards5` | BA Tasks | board relation |
| `connect_boards_mkkjmws6` | Payment requests list | board relation |
| `people` | People | people |
| `people8` | Watchers | people |
| `multiple_person` | QA | people |
| `subitems` | Subitems | subtasks |

Main `status_15` labels: `Working on it`, `Ready`, `OLD`, `Click for duplicate`, `Template`.

Main operational lifecycle (`color_mkv5jjn5`): `To Do`, `In Progress`, `Missing Art`, `Missing Config`, `Missing Art & Config`, `Missing MCP`, `Missing List`, `More Info Required`, `Risk`, `Ready for QA`, `QA In Progress`, `QA Done`, `QA'd needs ATTN`, `Ready for Payment`, `Payment Canceled`, `Ready to Publish`, `Scheduled`, `Internal`, `No action required`, `Done`, `Cancelled`, `M&M Completed`, `Delay`, `Archieve`.

## Operational subitem columns

These are the columns an automated task writer uses.

| Column ID | Title | Type | Write rule |
|---|---|---|---|
| `name` | Name | name | Concise promo/mechanic name; parent already carries the date |
| `date_mm0f8tdb` | Start date | date | Production start date |
| `date_mm0fr8sp` | End date | date | Production end date |
| `person` | Assignee | people | Leave blank unless assignment is known |
| `people_mkkfc9vj` | QA Assignee | people | Leave blank unless assignment is known |
| `dup__of_m_m_status1` | Operation Status | status | New draft: `To Do` |
| `status` | M&M Status | status | New draft: `M&M Completed` only after MM handoff is complete |
| `status8` | QA Priority | status | Set only from an explicit priority |
| `times_per_player__1` | Times per player | dropdown | `Once` or `Multiple` only when confirmed |
| `long_text` | Description | long_text | Execution-ready operational instructions |
| `date_mkp4d99c` | Due Date | date | Only if a separate preparation deadline is known |
| `files` | M&M Files | file | Attach config/art; never invent links |
| `text8` | Journey ID | text | Set only after Ops supplies it |
| `tags__1` | Layer | tags | Set only from an existing board taxonomy |
| `text5__1` | PM NOTES | text | Notes, not the execution brief |
| `connect_boards` | Economy Tasks | board relation | Link when economy/config approval exists |
| `connect_boards65` | BA Lists | board relation | Link when a BA list is required |
| `connect_boards__1` | Payment requests list | board relation | Link for payout work |
| `board_relation_mkzvrve9` | MM calendar | board relation | Link to the source calendar item when available |

Operation Status labels: `In Progress`, `Done`, `Missing Config`, `To Do`, `Risk`, `More Info required`, `QA Done`, `Scheduled`, `QA in Progress`, `Ready for QA`, `On hold`, `Missing art`, `Internal`, `Ready for Payment`, `Canceled`, `QA'd, needs ATTN`, `Ready to publish`, `Missing Art+config`, `No Action required`, `Missing List`, `Payment canceled`, `Missing MCP`, `General Issue with Promo`.

M&M Status labels include: `Operations in Progress`, `Done`, `Missing Config`, `Operations To Do`, `Risk`, `More Info required`, `Internal Task`, `M&M Completed`, `QA in Progress`, `Ready for QA`, `On hold`, `Missing art`, `Fill in LOR&A`, `Backup`, `Waiting for economy`, `M&M Delay`, `Ready to publish`, `MM Work in Progress`, `M&M Change`, `Cancelled`, `Missing Art+Config`, `Missing MCP`, `Missing List`, `Missing Test Groups`, `Postponed`, `Night Plan`, `After Promo`, `Ready for internal`, `MM in progress`.

## Observed task anatomy

### Standard offer/config task

```text
Start: 2026-03-04 at 12:00 UTC
End: 2026-03-05 at 12:00 UTC

Daily Deal with Coins + Gems + 8 Hammers + 1 GGS.
High pricing.
Multiple times per player.
```

### Journey/challenge task

```text
Start: <timestamp UTC>
End: <timestamp UTC>

Audience / exclusions: <confirmed segments>
Mechanic: <what the player must do>
Prize: <exact reward>
Times per player: Once | Multiple

Journey:
Trigger: <event>
Condition: <eligibility, if any>
Action 1: <system action>
Action 2: <reward / UI transition>

Surfaces and CTA:
- Login / banner / news feed / widget
- CTA target or parameter

Dependencies:
- Config: attached / missing
- Art: linked / missing
- MCP, list, economy or BA task: <confirmed link/status>
```

Do not fill unknown audience, parameters, journey IDs, files, MCP IDs, test groups, assignees, or numeric rewards. Mark them as `TBD - owner required` and use `More Info required` when the missing field blocks execution.

## Updates/comments

Updates are the collaboration and audit trail, not a substitute for the Description.

- MM/config change: state the exact change, effective UTC time, and @mention owners.
- Ops clarification: answer in the thread; then update Description if the execution contract changed.
- QA update: identify the promo/date, validation sample, expected requirement, result, and unresolved issues.
- Never generate a QA confirmation before QA actually happened.
- Never delete historical files or comments when a new config supersedes them; explicitly identify the effective version.

## Safe read/write pattern

1. Find the exact parent day by `Name == YYYY-MM-DD`.
2. Read all existing subitems for duplicate detection.
3. Match by normalized subitem name plus parent day.
4. Dry-run the proposed create/update and show all fields.
5. On explicit approval, create or update the subitem only.
6. Never delete, move, archive, assign people, attach files, or post comments without explicit scope.
7. If the parent day does not exist, stop unless creation of that day was explicitly authorized.
