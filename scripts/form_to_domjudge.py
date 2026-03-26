#!/usr/bin/env python3

import csv
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

GROUP_MAP = {
    "华师新生": (6, "校内新生"),
    "外校新生": (7, "校外新生"),
    "老灯": (8, "老生"),
}

SCHOOL_SHORT = {
    "华中师范大学": "CCNU",
    "武汉大学": "WHU",
    "华中科技大学": "HUST",
    "武汉理工大学": "WHUT",
    "湖北工业大学": "HUT",
    "华中农业大学": "HZAU",
    "武汉工程大学": "WIT",
    "湖北文理学院": "HBUAS",
    "湖北中医药大学": "HBTCM",
    "武昌理工学院": "WUT",
    "武汉科技大学": "WUST",
    "武汉商学院": "WBU",
    "武汉体育学院": "WHSU",
    "长江大学": "YZU",
    "中国地质大学（武汉）": "CUG",
    "中国地质大学": "CUG",
    "中南民族大学": "SCUEC",
    "武汉纺织大学": "WTU",
    "湖北大学": "HBU",
    "湖北第二师范学院": "HUE",
    "湖北经济学院": "HBUE",
    "湖北商贸学院": "HBC",
    "黄冈师范学院": "HGNU",
    "武汉学院": "WHXY",
    "江汉大学": "JHU",
    "华中师范大学武汉新城实验初级中学": "CCNUXC",
}

SCHOOL_FIXES = {
    ("杨晨", "25130217"): "湖北经济学院",
    ("杨少坡", "202413407181"): "武汉科技大学",
    ("付习之", "13"): "华中师范大学武汉新城实验初级中学",
}

ORGANIZATIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "organizations.json"

EXCLUDED_RECORDS = {
    ("赵程", "202521091048"),
    ("卢传恩", "24202170401"),
}

INVALID_EMAIL_SUFFIXES = (".con", ".edu")

REGISTRATIONS_HEADER = [
    "team_id",
    "category_id",
    "group_name",
    "team_name",
    "member_name",
    "school_name",
    "school_short",
    "username",
]

PASSWORD_SEED = 20250321
PASSWORD_LENGTH = 10
SEAT_SHUFFLE_SEED = 20250321
ROW_SHUFFLE_SEED = 20250321
DUPLICATE_KEYS = ["姓名", "学号", "QQ号", "邮箱"]


def clean(value: str) -> str:
    return " ".join((value or "").replace("\\r", " ").replace("\\n", " ").split())


def record_key(row: dict[str, str]) -> tuple[str, str]:
    return (clean(row["姓名"]), clean(row["学号"]))


def normalize_school(row: dict[str, str]) -> str:
    school = clean(row["所属学校"])
    other = clean(row["所属学校-其他-补充内容"])
    if school == "其他":
        if other:
            return other
        key = record_key(row)
        if key in SCHOOL_FIXES:
            return SCHOOL_FIXES[key]
        raise ValueError(f"missing school mapping for {key}")
    return school

def load_organization_ids() -> set[str]:
    organizations = json.loads(ORGANIZATIONS_PATH.read_text(encoding="utf-8"))
    return {clean(item["id"]) for item in organizations}


def username_pool(count: int) -> list[str]:
    seats = []
    for i in range(1, 65):
        seats.append(f"CCNU-A{i:02d}")
    for i in range(1, 65):
        seats.append(f"CCNU-B{i:02d}")
    for i in range(1, 31):
        seats.append(f"CCNU-C{i:02d}")
    if count > len(seats):
        raise ValueError(f"not enough seats for {count} teams")
    random.Random(SEAT_SHUFFLE_SEED).shuffle(seats)
    return seats[:count]


def generate_passwords(count: int) -> list[str]:
    rng = random.Random(PASSWORD_SEED)
    digits = "0123456789"
    return ["".join(rng.choice(digits) for _ in range(PASSWORD_LENGTH)) for _ in range(count)]


def dedupe_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    seen = set()
    result = []
    removed = 0
    for row in rows:
        key = (
            clean(row["姓名"]),
            clean(row["学号"]),
            clean(row["QQ号"]),
            clean(row["邮箱"]),
        )
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        result.append(row)
    return result, removed


def filter_excluded_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[tuple[str, str]]]:
    kept = []
    removed = []
    for row in rows:
        key = record_key(row)
        if key in EXCLUDED_RECORDS:
            removed.append(key)
            continue
        kept.append(row)
    return kept, removed


def filter_invalid_email_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[tuple[str, str, str]]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[record_key(row)].append(row)

    kept = []
    removed = []
    for key, items in grouped.items():
        has_valid_variant = any(not clean(item["邮箱"]).lower().endswith(INVALID_EMAIL_SUFFIXES) for item in items)
        for row in items:
            email = clean(row["邮箱"]).lower()
            if has_valid_variant and email.endswith(INVALID_EMAIL_SUFFIXES):
                removed.append((clean(row["姓名"]), clean(row["学号"]), clean(row["邮箱"])))
                continue
            kept.append(row)
    return kept, removed


def shuffle_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    shuffled = list(rows)
    random.Random(ROW_SHUFFLE_SEED).shuffle(shuffled)
    return shuffled


def build_registrations(rows: list[dict[str, str]], organization_ids: set[str]) -> list[dict[str, str]]:
    registrations = []
    usernames = username_pool(len(rows))
    for offset, row in enumerate(rows):
        original_group = clean(row["参赛组别"])
        if original_group not in GROUP_MAP:
            raise ValueError(f"unknown group: {original_group!r}")
        category_id, group_name = GROUP_MAP[original_group]
        school_name = normalize_school(row)
        if school_name not in SCHOOL_SHORT:
            raise ValueError(f"missing short name for school: {school_name}")
        school_short = SCHOOL_SHORT[school_name]
        if school_short not in organization_ids:
            raise ValueError(f"missing organization id for school: {school_name} ({school_short})")
        team_id = offset + 2
        member_name = clean(row["姓名"])
        registrations.append(
            {
                "team_id": str(team_id),
                "category_id": str(category_id),
                "group_name": group_name,
                "team_name": member_name,
                "member_name": member_name,
                "school_name": school_name,
                "school_short": school_short,
                "affiliation_external_id": school_short,
                "username": usernames[offset],
            }
        )
    return registrations


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)


def write_groups(path: Path) -> None:
    rows = [["File_Version", "1"]]
    for category_id, group_name in sorted({value for value in GROUP_MAP.values()}):
        rows.append([str(category_id), group_name])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerows(rows)


def write_teams(path: Path, registrations: list[dict[str, str]]) -> None:
    rows = [["File_Version", "2"]]
    for item in registrations:
        rows.append([
            item["team_id"],
            "",
            item["category_id"],
            item["team_name"],
            item["school_name"],
            item["school_short"],
            "CHN",
            item["affiliation_external_id"],
        ])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerows(rows)


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_accounts_yaml(path: Path, registrations: list[dict[str, str]]) -> None:
    passwords = generate_passwords(len(registrations))
    lines = []
    for item, password in zip(registrations, passwords, strict=True):
        lines.extend([
            f"- id: {item['team_id']}",
            f"  username: {yaml_scalar(item['username'])}",
            f"  password: {yaml_scalar(password)}",
            '  type: "team"',
            f"  name: {yaml_scalar(item['team_name'])}",
            f"  team_id: {item['team_id']}",
        ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_accounts_tsv(path: Path, registrations: list[dict[str, str]]) -> None:
    passwords = generate_passwords(len(registrations))
    rows = [["File_Version", "1"]]
    for item, password in zip(registrations, passwords, strict=True):
        rows.append([item["team_id"], item["username"], password, "team", item["team_name"], item["team_id"]])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerows(rows)


def validate(registrations: list[dict[str, str]]) -> None:
    team_ids = [item["team_id"] for item in registrations]
    usernames = [item["username"] for item in registrations]
    if len(team_ids) != len(set(team_ids)):
        raise ValueError("duplicate team_id detected")
    if len(usernames) != len(set(usernames)):
        raise ValueError("duplicate username detected")
    category_pairs = {(item["category_id"], item["group_name"]) for item in registrations}
    if len(category_pairs) != len({item["category_id"] for item in registrations}):
        raise ValueError("category_id to group_name mapping is not one-to-one")
    school_pairs = {(item["school_name"], item["school_short"]) for item in registrations}
    if len(school_pairs) != len({item["school_name"] for item in registrations}):
        raise ValueError("school_name to school_short mapping is not one-to-one")


def duplicate_summary(rows: list[dict[str, str]]) -> dict[str, dict[str, list[tuple[str, str]]]]:
    summary = {}
    for field in DUPLICATE_KEYS:
        seen = defaultdict(list)
        for row in rows:
            value = clean(row[field])
            if value:
                seen[value].append(record_key(row))
        summary[field] = {value: keys for value, keys in seen.items() if len(keys) > 1}
    return summary


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python form_to_domjudge.py input_form.csv output_dir")
        return 1

    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    unique_rows, removed_exact_duplicates = dedupe_rows(rows)
    filtered_rows, removed_excluded = filter_excluded_rows(unique_rows)
    filtered_rows, removed_invalid_email = filter_invalid_email_rows(filtered_rows)
    shuffled_rows = shuffle_rows(filtered_rows)
    organization_ids = load_organization_ids()
    registrations = build_registrations(shuffled_rows, organization_ids)
    validate(registrations)
    duplicates = duplicate_summary(filtered_rows)

    write_tsv(
        output_dir / "registrations.tsv",
        REGISTRATIONS_HEADER,
        [[item[key] for key in REGISTRATIONS_HEADER] for item in registrations],
    )
    write_groups(output_dir / "groups.tsv")
    write_teams(output_dir / "teams.tsv", registrations)
    write_accounts_yaml(output_dir / "accounts.yaml", registrations)
    write_accounts_tsv(output_dir / "accounts.tsv", registrations)

    print(f"raw_rows={len(rows)}")
    print(f"removed_exact_duplicates={removed_exact_duplicates}")
    print(f"removed_excluded={len(removed_excluded)}")
    for name, student_id in removed_excluded:
        print(f"  excluded={name} / {student_id}")
    print(f"removed_invalid_email={len(removed_invalid_email)}")
    for name, student_id, email in removed_invalid_email:
        print(f"  invalid_email={name} / {student_id} / {email}")
    print(f"generated_rows={len(registrations)}")
    print(f"output_dir={output_dir}")
    print("school_fixes=")
    for key, value in SCHOOL_FIXES.items():
        print(f"  {key[0]} / {key[1]} -> {value}")
    print("duplicate_summary=")
    for field in DUPLICATE_KEYS:
        values = duplicates[field]
        print(f"  {field}: {len(values)}")
        for value, keys in sorted(values.items()):
            print(f"    {value}: {keys}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
