data_str = "'北京大学\n北京\n|\n主管部门：\n教育部\n本科\n|\n“双一流”建设高校\n招生章程>\n中国人民大学\n北京\n|\n主管部门：\n教育部\n本科\n|\n“双一流”建设高校\n招生章程>\n清华大学\n北京\n|\n主管部门：\n教育部\n本科\n|\n“双一流”建设高校\n招生章程>\n......（省略部分文本）'"

data_list = []
blocks = data_str.split('招生章程>')
for block in blocks:
    parts = block.split('\n|\n')
    if len(parts) >= 5:
        school_name = parts[0].strip()
        region = parts[1].strip()
        department = parts[2].strip()
        education_level = parts[3].strip()
        is_double_first_class = '“双一流”建设高校' in block
        data_list.append({
            '学校名称': school_name,
            '所在区域': region,
            '主管部门': department,
            '教学层次': education_level,
            '是否双一流': is_double_first_class
        })

for item in data_list:
    print(item)