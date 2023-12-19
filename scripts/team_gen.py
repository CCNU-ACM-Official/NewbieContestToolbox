# Author: @a48zhang
# 2023/12/19

import argparse
import csv
import json

parser = argparse.ArgumentParser(
    prog="team_gen.py",
    description="""Generate teams information for DomJudge.
    CSV format: teamname, school, grade, schoolID(won't use), ID.
    """,
    epilog="If you are facing encoding problems, use the WSL.",
)

parser.add_argument("filename", metavar="input filename", type=str, help="the csv file")

parser.add_argument("output", metavar="output filename", type=str, help="the json file")

args = parser.parse_args()
filename = args.filename
output = args.output

schools = {
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
    "中南民族大学": "SCUEC",
    "武汉纺织大学": "WTU",
}

# position definition
pos = {"name": 0, "organization_id": 1, "group_ids": 2, "id": 4}


def deal_with_csv(filename):
    csv_reader = csv.reader(open(filename, encoding="utf8"))
    data = []
    for row in csv_reader:
        now = {}
        now.update({"name": row[pos["name"]]})
        if row[pos["group_ids"]] in schools:
            now.update({"organization_id": schools[row[pos["organization_id"]]]})
        else:
            now.update({"organization_id": "others"})

        # modify every year
        if row[pos["group_ids"]] == "2023" or row[pos["group_ids"]] == "2023级":
            now.update({"group_ids": ["participants"]})
        else:
            now.update({"group_ids": ["observers"]})

        now.update({"id": row[pos["id"]]})
        now["id"] = now["id"].replace("x", "X")
        now["id"] = now["id"].replace(" ", "")
        now["id"] = now["id"].replace("\t", "")

        data.append(now)
    return json.dumps(data, ensure_ascii=False).encode("unicode_escape").decode("utf-8")


open(output, "w").write(deal_with_csv(filename))
