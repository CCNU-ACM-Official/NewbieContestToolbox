---
name: domjudge-import-data
description: Prepare reusable DOMjudge import data starting from a normalized registrations.tsv intermediate table. Use when a user needs the required middle-table schema, category mapping, downstream file formats, validation rules, or import order for groups, teams, and team accounts.
---

# DOMjudge Import Data

Use this skill after raw sign-up data has already been cleaned into a normalized TSV. Keep one-off cleaning code out of the skill unless the user explicitly asks for implementation details.

## Scope

This skill covers:

- the required intermediate table shape
- how to derive DOMjudge category, team, and account import files
- validation rules before import
- the import order

This skill does not cover:

- ad hoc parsing of a specific form export
- contest-specific seat allocation logic
- one-time cleanup scripts for duplicated or dirty source rows

## Required Intermediate Table

The normalized source file is `registrations.tsv`.

Requirements:

- encoding: `UTF-8`
- delimiter: tab
- first row: header
- one row per final team/account to import
- no duplicate rows

Required columns, in this exact order:

```tsv
team_id	category_id	group_name	team_name	member_name	school_name	school_short	username
```

Column rules:

- `team_id`: unique positive integer used by DOMjudge teams and team accounts.
- `category_id`: integer category identifier. Keep it stable across all generated files.
- `group_name`: human-readable category name.
- `team_name`: team display name imported into DOMjudge.
- `member_name`: primary member name kept only for traceability and manual checks.
- `school_name`: normalized institution name.
- `school_short`: normalized institution short name such as `CCNU`, `WHU`, `HUST`.
- `username`: unique team login name.

Notes:

- Do not keep `status`, `country_code`, raw form row ids, QQ, email, or student id in this table unless a later task explicitly needs them.
- `country_code` is not source data here; render it downstream as a fixed constant, usually `CHN`.
- If this contest series uses fixed categories, keep them in `category_id` and `group_name`. For the current school contest convention, the default mapping is:

```tsv
1	校内新生
2	校外新生
3	老生
```

## Outputs

Generate these files from `registrations.tsv`:

1. `groups.tsv` or `groups.json`
2. `teams.tsv` in DOMjudge TSV v2 format
3. `accounts.yaml` for team accounts

Read [references/domjudge-formats.md](references/domjudge-formats.md) when the exact output schema or version compatibility matters.

## Generation Rules

### Categories

Derive category data from distinct pairs of `category_id` and `group_name`.

Requirements:

- each `category_id` maps to exactly one `group_name`
- sort by `category_id`
- never infer category ids after generation starts; assign them before rendering outputs

### Teams

Render one DOMjudge team row per `registrations.tsv` row.

Source mapping:

- team id: `team_id`
- category id: `category_id`
- team name: `team_name`
- institution name: `school_name`
- institution short name: `school_short`
- country code: constant `CHN` unless the contest explicitly spans multiple countries

Do not store blank external ids in the intermediate table. Fill those blanks only in the exported DOMjudge TSV.

### Accounts

Render one DOMjudge team account per `registrations.tsv` row.

Requirements:

- `username` comes from the intermediate table and must stay stable once accounts are distributed
- generate passwords at render time, not in the intermediate table
- account `type` is `team`
- account `team_id` must match the generated team file exactly
- account display `name` should normally equal `team_name`

If the target DOMjudge instance does not support `accounts.yaml`, generate the legacy TSV fallback described in [references/domjudge-formats.md](references/domjudge-formats.md).

## Validation

Before import, check all of the following:

- `team_id` is unique
- `username` is unique
- every row has non-empty `category_id`, `group_name`, `team_name`, `school_name`, `school_short`, and `username`
- `category_id` to `group_name` is one-to-one
- `school_name` to `school_short` is one-to-one within the dataset
- every account references an existing `team_id`
- rendered team and account row counts both equal the number of rows in `registrations.tsv`
- every `school_short` used by `teams.tsv` exists in the organization reference file if one is maintained

If the repository also maintains an organization reference file, update it only when a new `school_short` or normalized `school_name` appears. Do not duplicate organization data into the intermediate table.

## Server Preflight

Before uploading to a real DOMjudge instance, inspect the target server state:

- if organizations or affiliations already exist, verify their external ids match the repository `organizations.json` ids exactly
- do not accept server-generated ids such as `dj-2` when logos, branding, or downstream lookups depend on ids like `CCNU` or `WHUT`
- if the target server already has wrong affiliation ids, fix or rebuild those affiliations before trusting a team import test
- verify categories with the same names do not already exist under different numeric ids
- verify whether the server expects account import as YAML, JSON, or legacy TSV for its current DOMjudge version

## Import Order

Use this order when organizations are managed separately:

1. import organizations
2. import categories/groups
3. import teams
4. import accounts

If organizations are already present and already use the correct ids, skip step 1.

This avoids team imports referencing missing categories, teams binding to wrong affiliations, and account imports referencing missing teams.

## Common Pitfalls

- Leaving `external_institution_id` blank in `teams.tsv` will make DOMjudge create new affiliations instead of reusing the intended organizations.
- Reusing a server that already has affiliations whose external ids are `dj-*` can make teams appear to import correctly while still breaking logo lookup and any logic keyed by organization id.
- On DOMjudge 9, legacy `accounts.tsv` may be rejected even though older workflows used it successfully. Keep JSON or YAML account import available as a fallback.
- A successful team import does not prove the organization layer is correct. Always verify affiliation external ids on the server after import.

## Working Style

When asked to prepare DOMjudge import data:

1. verify that the source has already been normalized into `registrations.tsv`
2. confirm or assign the category mapping
3. render `groups.tsv`, `teams.tsv`, and `accounts.yaml`
4. run the validation checklist
5. report any unmapped schools, duplicate ids, or username collisions before import
