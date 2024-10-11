import csv
import pandas as pd

def read_markdown_table(file_path):
    """
    Read a markdown table from a file and return the data as a list of lists.
    
    Parameters:
    file_path (str): The path to the markdown file.
    
    Returns:
    list of lists: The data from the markdown table.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Find the start and end of the table
    start = False
    table_data = []
    for line in lines:
        if line.strip().startswith('|'):
            if start:
                columns = [col.strip() for col in line.strip('|\n').split('|')]
                table_data.append(columns)
            else:
                start = True
                columns = [col.strip() for col in line.strip('|\n').split('|')]
                table_data.append(columns)  # This is the header
        elif start:
            break  # Stop reading after the table ends
    
    return table_data

def markdown_table_to_csv(md_table, csv_file):
    """
    Convert a markdown table to CSV format and write to a file.
    
    Parameters:
    md_table (list of lists): The markdown table data.
    csv_file (str): The path to the CSV file to write.
    """
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(md_table)
def csv_to_excel(csv_file,excel_file):
    # 读取 CSV 文件
    data = pd.read_csv(csv_file)
    # 将数据写入 Excel 文件
    data.to_excel(excel_file, index=False)

# Example usage:
markdown_file_path = 'C:\\Users\\wonder\\Documents\\college-major4hs\\2024高考\\weici.md'  # Replace with your markdown file path
csv_file_path = 'C:\\Users\\wonder\\Documents\\college-major4hs\\2024高考\\weici.csv'  # Replace with your desired CSV file path
excel_file_path = 'C:\\Users\\wonder\\Documents\\college-major4hs\\2024高考\\weici.xlsx'

# Read the markdown table
md_table = read_markdown_table(markdown_file_path)

# Convert and write to CSV
markdown_table_to_csv(md_table, csv_file_path)
csv_to_excel(csv_file_path,excel_file_path)