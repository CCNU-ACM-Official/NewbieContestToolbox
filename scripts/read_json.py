# Author: @a48zhang
# 2023/12/19

import argparse
import json

parser = argparse.ArgumentParser(
    prog="read_json.py",
    description="""Print a json file.
    """,
)

parser.add_argument("filename", metavar="input filename", type=str, help="team.json")

args = parser.parse_args()

x = json.load(open(args.filename))
print(json.dumps(x, indent=4, sort_keys=True, ensure_ascii=False))
