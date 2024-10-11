from datetime import datetime
import time
import logging
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By

########## 爬取阳光高考高校名单和类型 ############
# 创建日志记录器
logging.basicConfig(level=logging.INFO)

def extract_school_data(scdata):
    name_element = scdata.find_element(By.CSS_SELECTOR, 'a.text-decoration-none.name')
    name = name_element.text
    depart_text = scdata.find_element(By.CSS_SELECTOR, 'a.sch-department').text
    locate = depart_text.split("\n|\n")[0].split("\n")[1]
    depart = depart_text.split("\n|\n")[1].split("：\n")[1]
    level_and_shuangyiliu_text = scdata.find_element(By.CSS_SELECTOR, 'a.sch-level').text
    level_and_shuangyiliu = level_and_shuangyiliu_text.split("\n|\n")
    level = level_and_shuangyiliu[0]
    isShuangyiliu = "Y" if len(level_and_shuangyiliu) > 1 else ""
    is985 = ""
    isMinban = ""
    isDuli = ""
    isZhongwai = ""
    isGangAO = ""
    sclink = name_element.get_attribute("href")
    return {
        "name": name,
        "locate": locate,
        "depart": depart,
        "level": level,
        "sclink": sclink,
        "isShuangyiliu": isShuangyiliu,
        "is985": is985,
        "isMinban": isMinban,
        "isDuli": isDuli,
        "isZhongwai": isZhongwai,
        "isGangAO": isGangAO
    }

def extract_data_from_page(driver):
    school_container = driver.find_element(By.CSS_SELECTOR, 'div.sch-list-container')
    school_datas = school_container.find_elements(By.CSS_SELECTOR, 'div.sch-item')
    return [extract_school_data(scdata) for scdata in school_datas]

def extract_special_data(driver, data_type):
    url_map = {
        "民办高校": "https://gaokao.chsi.com.cn/zsgs/zhangcheng/listVerifedZszc.do?method=index&yxmc=&ssdm=&yxls=&xlcc=&zgsx=&yxjbz=2",
        "独立学院": "https://gaokao.chsi.com.cn/zsgs/zhangcheng/listVerifedZszc.do?method=index&yxmc=&ssdm=&yxls=&xlcc=&zgsx=&yxjbz=3",
        "中外合作办学": "https://gaokao.chsi.com.cn/zsgs/zhangcheng/listVerifedZszc.do?method=index&yxmc=&ssdm=&yxls=&xlcc=&zgsx=&yxjbz=4",
        "内地与港澳合作办学": "https://gaokao.chsi.com.cn/zsgs/zhangcheng/listVerifedZszc.do?method=index&yxmc=&ssdm=&yxls=&xlcc=&zgsx=&yxjbz=5"
    }
    xpath_map = {
        "民办高校": "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/ul[1]/li[6]",
        "独立学院": "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/ul[1]/li[3]",
        "中外合作办学": "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/ul[1]/li[2]",
        "内地与港澳合作办学": "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/ul[1]/li[2]"        
    }
    driver.get(url_map[data_type])
    driver.set_window_size(1552, 832)
    time.sleep(1)
    page_num_text = driver.find_element(By.XPATH, xpath_map[data_type]).text
    total_pages = int(page_num_text)
    logging.info(f"{data_type}总页数：{total_pages}")
    data = extract_data_from_page(driver)
    for page in range(1, total_pages):
        logging.info(f'正在抓取第 {page + 1} 页')
        if page > 0:
            driver.find_element(By.CSS_SELECTOR, ".ivu-page-next").click()
            time.sleep(1)
            data.extend(extract_data_from_page(driver))
    return data

def mark_special_status(data_all, special_data, status_key):
    special_dict = {item["name"]: True for item in special_data}
    for item in data_all:
        if item["name"] in special_dict:
            item[status_key] = "Y"

def save_to_excel(data, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = ['学校名称', '所在区域', '主管部门', '办学层次', '双一流', '明细链接', '985', '民办高校', '独立学院', '中外合作办学', '内地与港澳台合作办学']
    ws.append(headers)
    for item in data:
        row_data = [item.get('name', ''), item.get('locate', ''), item.get('depart', ''), item.get('level', ''), item.get('isShuangyiliu', ''), item.get('sclink', ''), item.get("is985", ""), item.get("isMinban", ""), item.get("isDuli", ""), item.get("isZhongwai", ""), item.get("isGangAO", "")]
        ws.append(row_data)
    wb.save(filename)

def main():
    driver = webdriver.Chrome()
    try:
        driver.get("https://gaokao.chsi.com.cn/zsgs/zhangcheng/listVerifedZszc--method-index,ssdm-,yxls-,xlcc-,zgsx-,yxjbz-,start-0.dhtml")
        driver.set_window_size(1552, 832)
        time.sleep(1)
        page_num_text = driver.find_element(By.XPATH, '/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/ul[1]/li[6]').text
        total_pages = int(page_num_text)
        logging.info(f"总页数：{total_pages}")
        data_all = extract_data_from_page(driver)
        for page in range(1, total_pages):
            logging.info(f'正在抓取第 {page + 1} 页')
            if page > 0:
                driver.find_element(By.CSS_SELECTOR, ".ivu-page-next").click()
                time.sleep(1)
                data_all.extend(extract_data_from_page(driver))

        # 处理 985 高校名单
        data_985 = [
            {"name": "北京大学"},
            {"name": "清华大学"},
            {"name": "中国人民大学"},
            {"name": "北京航空航天大学"},
            {"name": "北京师范大学"},
            {"name": "北京理工大学"},
            {"name": "中央民族大学"},
            {"name": "中国农业大学"},
            {"name": "上海交通大学"},
            {"name": "复旦大学"},
            {"name": "华东师范大学"},
            {"name": "同济大学"},
            {"name": "中南大学"},
            {"name": "湖南大学"},
            {"name": "国防科技大学"},
            {"name": "西安交通大学"},
            {"name": "西北工业大学"},
            {"name": "西北农林科技大学"},
            {"name": "南京大学"},
            {"name": "东南大学"},
            {"name": "天津大学"},
            {"name": "南开大学"},
            {"name": "四川大学"},
            {"name": "电子科技大学"},
            {"name": "东北大学"},
            {"name": "大连理工大学"},
            {"name": "中山大学"},
            {"name": "华南理工大学"},
            {"name": "山东大学"},
            {"name": "中国海洋大学"},
            {"name": "武汉大学"},
            {"name": "华中科技大学"},
            {"name": "浙江大学"},
            {"name": "吉林大学"},
            {"name": "厦门大学"},
            {"name": "重庆大学"},
            {"name": "兰州大学"},
            {"name": "中国科学技术大学"},
            {"name": "哈尔滨工业大学"}
        ]
        dict_985 = {item["name"]: True for item in data_985}
        for item in data_all:
            if item["name"] in dict_985:
                item["is985"] = "Y"

        # 处理其他特殊类型数据
        special_types = ["民办高校", "独立学院", "中外合作办学", "内地与港澳合作办学"]
        types_map = {"民办高校":"isMinban","独立学院":"isDuli","中外合作办学":"isZhongwai","内地与港澳合作办学":"isGangAO"}
        for data_type in special_types:
            special_data = extract_special_data(driver, data_type)
            mark_special_status(data_all, special_data, types_map[data_type])

        current_date = datetime.now().strftime('%Y%m%d')
        save_to_excel(data_all, f'C:\\Users\\wonder\\Documents\\college-major4hs\\教育部\\yangguanggaokao_{current_date}.xlsx')

    finally:
        driver.quit()

if __name__ == "__main__":
    main()