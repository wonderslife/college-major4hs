import pandas as pd
import os
import json

# 读取 xlsx 文件
df_xlsx = pd.read_excel('C:\\Users\\wonder\\Documents\\college-major4hs\\教育部\\yangguanggaokao_20241003.xlsx')

# 获取目录下符合条件的 json 文件列表
directory = '教育部\\qa'
json_files = [f for f in os.listdir(directory) if f.startswith('qa-') and f.endswith('.json')]

# 收集所有 json 文件中的 schoolName
school_names_json = set()
for json_file in json_files:
    file_path = os.path.join(directory, json_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            if 'schoolName' in item:
                school_names_json.add(item['schoolName'])

# 在 xlsx 的学校名称中找出不在 json 文件中的行
missing_rows = df_xlsx[~df_xlsx['学校名称'].isin(school_names_json)]

# 将这些行保存到新的 excel 文件
missing_rows.to_excel('教育部\\qa_missing_schools.xlsx', index=False)