import openpyxl
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)

def match_and_write_results(source_file, target_file):
    # 加载评估结果文件
    try:
        wb_source = openpyxl.load_workbook(source_file)
        sheet_source = wb_source.active
        logging.info("加载评估结果文件 ")
    except Exception as e:
        logging.error(f"无法加载评估结果文件 {source_file}: {e}")
        return

    # 加载目标文件，并将数据存储在字典中
    target_data = {}
    try:
        wb_target = openpyxl.load_workbook(target_file)
        sheet_target = wb_target.active
        logging.info("加载目标文件")
        for index,row in sheet_target.iter_rows(min_row=2, values_only=True):
            school_name = row[2]
            major_code = row[3]
            target_data[(school_name, major_code)] = index
    except Exception as e:
        logging.error(f"无法加载目标文件 {target_file}: {e}")
        return

    # 遍历评估结果文件的每一行
    for row in sheet_source.iter_rows(min_row=2, values_only=True):
        school_name = row[0]
        major_code = row[1]  # 学科代码
        evaluation_result = row[3]  # 评估结果

        # 在目标文件中查找匹配的学校和专业
        found = False
        key = (school_name, major_code)
        if key in target_data:
            target_row_index = target_data[key]
            # 将评估结果写入目标文件的第9列
            sheet_target.cell(row=target_row_index, column=9, value=evaluation_result)
            found = True
            logging.info(f"找到匹配的学校和专业: 学校 {school_name}, 专业代码 {major_code}, 评估 {evaluation_result}")
        else:
            logging.warning(f"未找到匹配的学校和专业: 学校 {school_name}, 专业代码 {major_code}")

    # 保存修改后的目标文件
    try:
        wb_target.save(target_file)
    except Exception as e:
        logging.error(f"保存目标文件 {target_file} 时出错: {e}")

if __name__ == "__main__":
    source_file = "教育部\\4.5_evaluation.xlsx"
    target_file = "2024高考\\2024招生专业评估.xlsx"
    match_and_write_results(source_file, target_file)