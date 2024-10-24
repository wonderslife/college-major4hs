from openpyxl import load_workbook
import openpyxl

def split_professions(file_path):
    # 加载工作簿
    wb = load_workbook(file_path)
    sheet = wb.active

    # 用于存储拆分后的所有行数据
    new_rows = []

    # 遍历每一行
    for row in sheet.iter_rows():
        # 假设包含专业代码及名称的列名为"包含专业代码及名称"，你可以根据实际情况修改
        profession_column_name = "包含专业代码及名称"
        column_index = None
        for column in sheet.columns:
            if column[0].value == profession_column_name:
                column_index = column[0].column
                break
            if column_index is not None:
                # 在此处使用列索引进行操作
                if row[column_index] is not None:
            # 你的现有代码
                    profession_values = row[sheet.columns[profession_column_name]].value.split(';')
                    for profession_value in profession_values:
                        new_row = []
                        for cell in row:
                            new_row.append(cell.value)
                        new_row[sheet.columns[profession_column_name].number] = profession_value
                        new_rows.append(new_row)

    # 创建新的工作簿来存储拆分后的结果
    new_wb = openpyxl.Workbook()
    new_sheet = new_wb.active

    # 将拆分后的行数据写入新的工作簿
    for row in new_rows:
        new_sheet.append(row)

    # 保存新的工作簿
    new_wb.save('split_professions.xlsx')

file_path = '教育部\\2024高校本科专业目录.xlsx'

split_professions(file_path)