# Author: @a48zhang
# 2025/03/21

import csv
import sys
import random
import string
import yaml

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
    "中国地质大学": "CUG", # 666
    "中南民族大学": "SCUEC",
    "武汉纺织大学": "WTU",
    "湖北大学": "HBU",
    "湖北第二师范学院": "HUE",
    "湖北经济学院": "HBUE",
    "湖北商贸学院": "HBC",
    "黄冈师范学院": "HGNU",
    "武汉学院": "WHXY",
}

def generate_password(length=10):
    characters =string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def main():
    if len(sys.argv) != 4:
        print("Usage: python account_gen.py input.csv output.yaml")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    out2 = sys.argv[3]
    
    teams = []
    current_id = 2

    seats = []
    for i in range(1, 30):
        seats.append(f"CCNU-A{i:02d}")
        seats.append(f"CCNU-B{i:02d}")
        seats.append(f"CCNU-C{i:02d}")
    for i in range(31, 72):
        seats.append(f"CCNU-A{i:02d}")
    random.shuffle(seats)


    t = 2
    groups = dict()
    sch = dict()
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for row in reader:
            original_id, group, name, school = row
            school_short = schools[school]
            
            
            username = seats[0]
            seats.remove(username)
            groups[username] = group
            sch[username] = school

            team = {
                "id": current_id,
                "username": username,
                "password": generate_password(),
                "type": "team",
                "name": name,
                "team_id" : t
            }
            teams.append(team)
            current_id += 1
            t += 1
            
    with open(out2, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(['File_Version', '2'])
        for te in teams:
            output_row = [
                te['team_id'],        # Team ID
                te['username'], # External ID（空）
                groups[te['username']],    # Category ID
                te['name'],      # Team Name
                sch[te['username']],    # Institution Name
                schools[sch[te['username']]],     # Institution Short Name
                'CHN',          # Country Code
                ''              # External Institution ID（空）
            ]
            
            writer.writerow(output_row)

    
    # 生成YAML格式
    with open(output_file, 'w', encoding='utf-8') as outfile:
        yaml.dump(teams, outfile, 
                 default_flow_style=False, 
                 allow_unicode=True,
                 sort_keys=False,
                 indent=2)

if __name__ == "__main__":
    main()
