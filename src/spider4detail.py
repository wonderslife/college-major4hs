import json
import logging
import time
import openpyxl
import os
import qianfan
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from datetime import datetime

def extract_school_info(driver, zsjz_digest, zsjz_link1):
    try:
        name = driver.find_element(By.CSS_SELECTOR, "a.name.yxmc").text
    except NoSuchElementException:
        name = ""
    try:
        follow = driver.find_element(By.CSS_SELECTOR, "span.followCount").text
    except NoSuchElementException:
        follow = ""
    try:
        location = driver.find_element(By.CSS_SELECTOR, "span.txdz").text
    except NoSuchElementException:
        location = ""
    try:
        official_website = driver.find_element(By.CSS_SELECTOR, "a.gfwz").get_attribute("href")
    except NoSuchElementException:
        official_website = ""
    try:
        admission_website = driver.find_element(By.CSS_SELECTOR, "a.zswz").get_attribute("href")
    except NoSuchElementException:
        admission_website = ""
    try:
        phone = driver.find_element(By.CSS_SELECTOR, "span.gfdh").text
    except NoSuchElementException:
        phone = ""
    try:
        wx = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]").text
    except NoSuchElementException:
        wx = ""
    try:
        # 微信视频号
        wxshipin = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]").text
    except NoSuchElementException:
        wxshipin = ""
    return {
        "name": name,
        "location": location,
        "follow": follow,
        "official_website": official_website,
        "admission_website": admission_website,
        "phone": phone,
        "zsjz_link": zsjz_link1,
        "zsjz_digest": zsjz_digest,
        "wx": wx,
        "wxshipin": wxshipin
    }

def extract_satisfaction_info(driver):
    try:
        items = driver.find_elements(By.CSS_SELECTOR, 'div.left-part.yxmyd-part li')
    except NoSuchElementException:
        items = []
    overall_satisfaction = {}
    environment_satisfaction = {}
    life_satisfaction = {}
    for item in items:
        try:
            satisfaction_name = item.find_element(By.CSS_SELECTOR, '.yxk-myd-name').text
            vote_num = item.find_element(By.CSS_SELECTOR, '.yxk-myd-num').text
            score = item.find_element(By.CSS_SELECTOR, '.yxk-myd-echarts').get_attribute('data-id')
        except NoSuchElementException:
            continue
        if satisfaction_name == "综合满意度":
            overall_satisfaction = {'vote_num': vote_num.replace("人投票", ""), 'score': score}
        if satisfaction_name == "环境满意度":
            environment_satisfaction = {'vote_num': vote_num.replace("人投票", ""), 'score': score}
        if satisfaction_name == "生活满意度":
            life_satisfaction = {'vote_num': vote_num.replace("人投票", ""), 'score': score}

    try:
        major_items = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div[2]/div[1]/div[4]").find_elements(By.CSS_SELECTOR, "div.zy-part-item")
    except NoSuchElementException:
        major_items = []
    major_satisfaction = {}
    for items in major_items:
        try:
            major_name = items.find_element(By.CSS_SELECTOR, "span.name").text
            major_score = items.find_element(By.CSS_SELECTOR, "span.rank").text
            major_voters = items.find_element(By.CSS_SELECTOR, "span.total").text
        except NoSuchElementException:
            continue
        major_satisfaction[major_name] = {"satisfication_score": major_score, "voters": major_voters.replace("（", "").replace("）", "").replace("人", "")}

    try:
        recommand_items = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div[2]/div[1]/div[6]").find_elements(By.CSS_SELECTOR, "div.zy-part-item")
    except NoSuchElementException:
        recommand_items = []
    major_recommand = {}
    for items in recommand_items:
        try:
            recommand_major_name = items.find_element(By.CSS_SELECTOR, "span.name").text
            recommand_major_score = items.find_element(By.CSS_SELECTOR, "span.rank").text
            recommand_major_voters = items.find_element(By.CSS_SELECTOR, "span.total").text
        except NoSuchElementException:
            continue
        major_recommand[recommand_major_name] = {"recommand_score": recommand_major_score, "recommand_voters": recommand_major_voters.replace("（", "").replace("）", "").replace("人", "")}

    try:
        prefer_items = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div[2]/div[1]/div[8]").find_elements(By.CSS_SELECTOR, "div.zy-part-item")
    except NoSuchElementException:
        prefer_items = []
    major_prefer = {}
    for items in prefer_items:
        try:
            prefer_major_name = items.find_element(By.CSS_SELECTOR, "span.name").text
            prefer_major_score = items.find_element(By.CSS_SELECTOR, "span.rank").text
            prefer_major_voters = items.find_element(By.CSS_SELECTOR, "span.total").text
        except NoSuchElementException:
            continue
        major_prefer[prefer_major_name] = {"recommand_score": prefer_major_score, "recommand_voters": prefer_major_voters.replace("（", "").replace("）", "").replace("人", "")}
    return {
        "overall_satisfaction": overall_satisfaction,
        "environment_satisfaction": environment_satisfaction,
        "life_satisfaction": life_satisfaction,
        "major_satisfaction": major_satisfaction,
        "major_recommand": major_recommand,
        "major_prefer": major_prefer
    }

logging.basicConfig(level=logging.INFO)

# 初始化浏览器驱动
driver = webdriver.Chrome()
#file_name = '教育部\yangguanggaokao_20241003.xlsx'
file_name = '教育部\detail_missing_schools.xlsx'
# 打开 Excel 文件
wb = openpyxl.load_workbook(file_name)
ws = wb.active

file_count = 0
combined_data = []
batch = 20

# 循环读取 sclink 字段的值并打开链接
for index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=1):
    # qianfan每25个随机休息2-10秒
    if index % 25 == 0:
        sleep_time = random.randint(2, 10)
        logging.info(f'正在休息 {sleep_time} 秒')
        time.sleep(sleep_time)
    sclink = row[5]
    name = row[0]
    logging.info(f"正在解析 {name} 的招生简章，明细链接:{sclink}")
    if sclink:
        # 在这里可以进行对打开页面的操作
        #driver.get(sclink)
        scid = sclink.split("/")[-1].split("--")[1]
        zsjz_link = "https://gaokao.chsi.com.cn/zsgs/zhangcheng/listZszc--" + scid
        logging.info(f'正在解析 {zsjz_link} 的招生简章')

        driver.get(zsjz_link)

        driver.set_window_size(1552, 832)
        time.sleep(1)
        try:
            zszc_link = driver.find_element(By.CSS_SELECTOR, "a.zszc-zc-title").get_attribute("href")
            driver.get(zszc_link)
            time.sleep(1)
            page_text = driver.find_element(By.TAG_NAME, "body").text

            # 替换下列示例中参数，安全认证Access Key替换your_iam_ak，Secret Key替换your_iam_sk，如何获取请查看https://cloud.baidu.com/doc/Reference/s/9jwvz2egb
            os.environ["QIANFAN_ACCESS_KEY"] = "cd8b9ae5abc748c7a69066ab5c264376"
            os.environ["QIANFAN_SECRET_KEY"] = "e384b45b9d974721a0f5d1c1e3dd22ab"

            chat_comp = qianfan.ChatCompletion()

            prompt = "你是一个经验丰富的归纳者,请用300字突出其中的关键信息,包括报考、招生、录取、体检、收费、毕业、就业、其他要求等内容:"

            # 指定特定模型
            resp = chat_comp.do(model="ERNIE-Speed-128K", messages=[{
                "role": "user",
                "content": prompt + page_text
            }])

            digest_text = resp["body"].get("result")

        except NoSuchElementException:
            digest_text = ""
            zszc_link = "无"

        # 获取学校基本信息和满意度信息
        driver.get(sclink)
        driver.set_window_size(1552, 832)
        time.sleep(1)
        school_info = extract_school_info(driver,digest_text,zsjz_link)
        satisfaction_info = extract_satisfaction_info(driver)

        sc_detail = {
            "SchoolInfo": {
                "schoolName": name,
                "BasicInfo": school_info,
                "Satisfaction": satisfaction_info
            }
        }

        combined_data.append(sc_detail)

        if index % batch == 0:
            current_date = datetime.now().strftime('%Y%m%d%H%M%S')
            with open(f'C:\\Users\\wonder\\Documents\\college-major4hs\\教育部\\school_detail\\combined-{current_date}-{file_count}.json', 'w', encoding='utf-8') as json_file:
                json.dump(combined_data, json_file, ensure_ascii=False, indent=4)
            file_count += 1
            combined_data = []

# 关闭浏览器
driver.quit()

# 如果最后不足 batch 个也保存一个文件
if combined_data:
    current_date = datetime.now().strftime('%Y%m%d%H%M%S')
    with open(f'C:\\Users\\wonder\\Documents\\college-major4hs\\教育部\\school_detail\\combined-{current_date}-{file_count}.json', 'w', encoding='utf-8') as json_file:
        json.dump(combined_data, json_file, ensure_ascii=False, indent=4)