from openpyxl import load_workbook

def convert_number_to_string(file_path):
    # 加载工作簿
    wb = load_workbook(file_path)

    # 遍历所有工作表
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]

        # 遍历所有行和列
        for row in sheet.iter_rows():
            for cell in row:
                # 如果单元格的值是数值类型，则将其转换为字符串类型
                if isinstance(cell.value, (int, float)):
                    cell.value = str(cell.value)

    # 保存修改后的工作簿
    wb.save(file_path)

# 调用函数进行转换
file_path = '教育部\\2024高校本科专业目录.xlsx'  # 替换为实际的文件路径
convert_number_to_string(file_path)