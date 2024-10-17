import pandas as pd
import json

with open('教育部\\1.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    
rows = []
for school, majors in data.items():
    for major, grade in majors.items():
        rows.append([school, major, grade])

df = pd.DataFrame(rows, columns=["学校名称", "专业", "评级"])
df.to_excel("教育部\第五次评价.xlsx", index=False)