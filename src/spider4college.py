from datetime import datetime
import time
import logging
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By

######### 爬取国家政务服务网高校清单 ############
# 创建日志记录器
logging.basicConfig(level=logging.INFO)

def extract_data_from_page(driver):
    table = driver.find_element(By.CSS_SELECTOR, "table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[0].text == "学校名称":
            continue
        data_item = {
            "name": cells[0].text if len(cells) > 0 else '',
            "incharge": cells[1].text if len(cells) > 1 else '',
            "region": cells[2].text if len(cells) > 2 else '',
            "hier": cells[3].text if len(cells) > 3 else ''
        }
        data.append(data_item)
    return data

def save_to_excel(data, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = ['学校名称', '主管部门', '所在地区', '办学层次']
    ws.append(headers)
    for item in data:
        row_data = [item.get('name', ''), item.get('incharge', ''), item.get('region', ''), item.get('hier', '')]
        ws.append(row_data)
    wb.save(filename)

def main():
    driver = webdriver.Chrome()
    try:
        driver.get("https://gjzwfw.www.gov.cn/fwmh/school/indexSchool.do")
        driver.set_window_size(1552, 832)
        time.sleep(1)
        
        # 从页面中提取总页数
        page_num_text = driver.find_element(By.CSS_SELECTOR, ".page_num").text
        total_pages = int(page_num_text.split("共")[1].split("页")[0])
        logging.info(f"总页数：{total_pages}")

        data_list = extract_data_from_page(driver)

        for page in range(1, total_pages):
            logging.info(f'正在抓取第 {page + 1} 页')
            if page > 0:
                driver.find_element(By.LINK_TEXT, "下一页>").click()
                time.sleep(1)
            data_list.extend(extract_data_from_page(driver))

        current_date = datetime.now().strftime('%Y%m%d')
        save_to_excel(data_list, f'C:\\Users\\wonder\\Documents\\college-major4hs\\教育部\\college_{current_date}.xlsx')

    finally:
        driver.quit()

if __name__ == "__main__":
    main()