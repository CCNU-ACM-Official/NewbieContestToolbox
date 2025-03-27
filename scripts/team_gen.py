# Author: @a48zhang
# 2025/03/21

import csv
import sys



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

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv2tsv.py input.csv output.tsv")
        return
    
    in_file = sys.argv[1]
    out_file = sys.argv[2]

    with open(in_file, 'r', encoding='utf-8') as infile, \
         open(out_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')
        
        # 写入文件头
        writer.writerow(['File_Version', '2'])
        
        for row in reader:
            team_id, category_id, team_name, institution = row
            short_name = schools[institution]
            
            # 构造输出行（注意空字段的位置）
            output_row = [
                team_id,        # Team ID
                '',             # External ID（空）
                category_id,    # Category ID
                team_name,      # Team Name
                institution,    # Institution Name
                short_name,     # Institution Short Name
                'CHN',          # Country Code
                ''              # External Institution ID（空）
            ]
            
            writer.writerow(output_row)

if __name__ == '__main__':
    main()
