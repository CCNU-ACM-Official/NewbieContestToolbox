# DOMjudge Output Formats

Use this reference only when exact file schemas or DOMjudge version compatibility matter.

Official documentation:

- DOMjudge Import and Export manual: https://www.domjudge.org/docs/manual/main/import.html
- DOMjudge Teams file format: https://www.domjudge.org/docs/manual/main/import.html#teams
- DOMjudge Accounts file format: https://www.domjudge.org/docs/manual/main/import.html#accounts

## Groups TSV

For TSV import, render one row per category after a header row:

```tsv
File_Version	1
1	校内新生
2	校外新生
3	老生
```

Each data row is:

```text
group_id<TAB>group_name
```

## Teams TSV v2

The repository's existing scripts emit TSV v2 team data. The content format is:

```tsv
File_Version	2
2		1	选手甲	华中师范大学	CCNU	CHN
3		2	选手乙	武汉理工大学	WHUT	CHN
4		3	选手丙	武汉大学	WHU	CHN
```

Each data row is:

```text
team_id<TAB>external_id<TAB>category_id<TAB>team_name<TAB>institution_name<TAB>institution_short_name<TAB>country_code<TAB>external_institution_id
```

Practical rules:

- keep `external_id` blank unless another system already provides a stable external identifier
- if organizations are imported separately, `external_institution_id` should use the `id` field from `organizations.json` for the matching school, such as `CCNU` or `WHU`
- `external_institution_id` must point to the organization id that the target server actually stores; if the server still uses wrong ids such as `dj-2`, logo lookup and any organization-id-based integration will stay broken until the affiliation ids themselves are corrected
- leaving `external_institution_id` blank will cause DOMjudge to create a new affiliation instead of reusing an existing organization
- use `CHN` as the rendered country code when the contest is domestic
- DOMjudge documentation may refer to this file as `teams2.tsv`; local repositories may still call it `teams.tsv`

## Accounts YAML

Preferred account import format for newer DOMjudge versions:

```yaml
- id: 2
  username: CCNU-A01
  password: 1234567890
  type: team
  name: 选手甲
  team_id: 2
- id: 3
  username: CCNU-B07
  password: 0987654321
  type: team
  name: 选手乙
  team_id: 3
```

Required fields per account object:

- `id`
- `username`
- `password`
- `type`
- `name`
- `team_id`

Rules:

- use `type: team`
- keep `team_id` equal to the imported DOMjudge team id
- keep account ids unique within the file
- generate passwords outside the intermediate table

## Legacy Accounts TSV Fallback

If the target instance only supports TSV account import, render:

```tsv
File_Version	1
2	CCNU-A01	1234567890	team	选手甲	2
3	CCNU-B07	0987654321	team	选手乙	3
```

Each data row is:

```text
account_id<TAB>username<TAB>password<TAB>type<TAB>name<TAB>team_id
```

Use this fallback only when the deployed DOMjudge version actually accepts this legacy shape.

Compatibility note:

- DOMjudge 9 may reject older `accounts.tsv` workflows even when the row shape looks correct.
- If TSV account import fails on a newer server, convert the same account objects to JSON and import them through the `accounts` JSON importer, or use the server's accepted YAML path when available.
