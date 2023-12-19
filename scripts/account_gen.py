# Author: @a48zhang
# 2023/12/19

import argparse
import json

parser = argparse.ArgumentParser(
    prog="account_gen.py",
    description="""Generate accounts information for DomJudge.
    Use team_gen.py first.
    """,
    epilog="If you are facing encoding problems, use the WSL.",
)

parser.add_argument("filename", metavar="input filename", type=str, help="team.json")

parser.add_argument("output", metavar="output filename", type=str, help="output.json")

args = parser.parse_args()

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

"""
id: the account ID. Must be unique

username: the account username. Must be unique

password: the password to use for the account

type: the user type, one of team, judge, admin or balloon, jury will be interpret as judge

team_id: (optional) the ID of the team this account belongs to

name: (optional) the full name of the account

ip (optional): IP address to link to this account
"""


def pwd(id):
    import random

    x = random.randint(10000, 99999)
    return "pwd" + id[-1:-4:-1] + str(x)


filename = args.filename
output = args.output

file = open(filename, "r")
js = json.loads(file.read())


def gen(js):
    data = []
    names = set()
    for item in js:
        now = {
            "username": item["name"],
            "id": item["id"],
            "team_id": item["id"],
            "type": "team",
            "password": pwd(item["id"]),
        }
        if now["username"] in names:
            now["username"] = now["username"] + now["id"][0:3]
        names.add(now["username"])
        data.append(now)

    return json.dumps(data, ensure_ascii=False).encode("unicode_escape").decode("utf-8")


open(output, "w").write(gen(js))
